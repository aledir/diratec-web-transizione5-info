import { useState, useEffect } from 'react';
import { useAuthContext } from '@/contexts/auth-context';

// Tipi
interface Lead {
  id: number;
  azienda: string;
  email: string;
  score: number;
  stato: string;
  data_creazione: string;
}

interface LeadDetail {
  id: number;
  azienda_data: {
    nome_azienda?: string;
    dimensione?: string;
    settore?: string;
    regione?: string;
  };
  investimenti_data: {
    tipo_investimento?: string;
    budget?: string;
    tempistiche?: string;
    descrizione_progetto?: string;
  };
  contatto_data: {
    nome?: string;
    cognome?: string;
    ruolo?: string;
    email?: string;
    telefono?: string;
  };
  fonte: string;
  data_creazione: string;
  score: number;
  stato: string;
  assegnato_a?: string;
  note?: string;
}

export default function LeadsDashboard() {
  // Stati
  const [leads, setLeads] = useState<Lead[]>([]);
  const [selectedLeadId, setSelectedLeadId] = useState<number | null>(null);
  const [selectedLead, setSelectedLead] = useState<LeadDetail | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [statusFilter, setStatusFilter] = useState<string>('tutti');
  const [filterText, setFilterText] = useState<string>('');
  const [isDetailLoading, setIsDetailLoading] = useState(false);
  const [isEditingNote, setIsEditingNote] = useState(false);
  const [noteText, setNoteText] = useState('');
  const { authToken, isAuthenticated } = useAuthContext();

  // Effetto per caricare i lead
  useEffect(() => {
    const fetchLeads = async () => {
      try {
        setIsLoading(true);
        
        if (!isAuthenticated) {
          setError('Autenticazione richiesta');
          setIsLoading(false);
          return;
        }
        
        const response = await fetch('https://api.transizione5.info/api/leads', {
          headers: {
            'Authorization': `Bearer ${authToken}`
          }
        });
        
        if (!response.ok) {
          throw new Error(`Errore API (${response.status})`);
        }
        
        const data = await response.json();
        
        if (data.error) {
          setError(data.error);
        } else {
          setLeads(data.leads || []);
          setError(null);
        }
      } catch (err) {
        setError('Impossibile recuperare i lead. Riprova più tardi.');
        console.error('Errore nel recupero dei lead:', err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchLeads();
  }, [authToken, isAuthenticated]);
  
  // Effetto per caricare i dettagli del lead selezionato
  useEffect(() => {
    const fetchLeadDetails = async () => {
      try {
        if (!selectedLeadId || !isAuthenticated) return;
        
        setIsDetailLoading(true);
        
        const response = await fetch(`https://api.transizione5.info/api/lead/${selectedLeadId}`, {
          headers: {
            'Authorization': `Bearer ${authToken}`
          }
        });
        
        if (!response.ok) {
          throw new Error(`Errore API (${response.status})`);
        }
        
        const data = await response.json();
        
        if (data.error) {
          throw new Error(data.error);
        } else {
          setSelectedLead(data);
          setNoteText(data.note || '');
        }
      } catch (err) {
        console.error('Errore nel recupero dei dettagli del lead:', err);
      } finally {
        setIsDetailLoading(false);
      }
    };

    fetchLeadDetails();
  }, [selectedLeadId, authToken, isAuthenticated]);
  
  // Funzione per aggiornare lo stato del lead
  const updateLeadStatus = async (leadId: number, newStatus: string) => {
    try {
      if (!isAuthenticated) return false;
      
      const response = await fetch(`https://api.transizione5.info/api/lead/update/${leadId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${authToken}`
        },
        body: JSON.stringify({ stato: newStatus })
      });
      
      if (!response.ok) {
        throw new Error(`Errore API (${response.status})`);
      }
      
      const data = await response.json();
      
      if (data.error) {
        throw new Error(data.error);
      }
      
      // Aggiorna la lista dei lead
      setLeads(leads.map(lead => 
        lead.id === leadId ? { ...lead, stato: newStatus } : lead
      ));
      
      // Aggiorna il lead selezionato se è quello modificato
      if (selectedLead && selectedLead.id === leadId) {
        setSelectedLead({ ...selectedLead, stato: newStatus });
      }
      
      return true;
    } catch (err) {
      console.error('Errore nell\'aggiornamento dello stato del lead:', err);
      return false;
    }
  };
  
  // Filtra i lead in base ai filtri attivi
  const filteredLeads = leads.filter(lead => {
    const matchesStatus = statusFilter === 'tutti' || lead.stato === statusFilter;
    const matchesText = !filterText || 
      (lead.azienda && lead.azienda.toLowerCase().includes(filterText.toLowerCase())) ||
      (lead.email && lead.email.toLowerCase().includes(filterText.toLowerCase()));
    
    return matchesStatus && matchesText;
  });
  
  // Ottiene il colore in base allo stato del lead
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'qualificato':
        return 'bg-green-100 text-green-800';
      case 'interessante':
        return 'bg-blue-100 text-blue-800';
      case 'da approfondire':
        return 'bg-yellow-100 text-yellow-800';
      case 'convertito':
        return 'bg-purple-100 text-purple-800';
      case 'non interessato':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };
  
  // Formatta la data
  const formatDate = (dateString: string) => {
    try {
      const date = new Date(dateString);
      return new Intl.DateTimeFormat('it-IT', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      }).format(date);
    } catch (e) {
      return dateString;
    }
  };
  
  // Se non autenticato, mostra un messaggio di avviso
  if (!isAuthenticated) {
    return (
      <div className="p-4 bg-yellow-50 rounded-lg border border-yellow-200 text-yellow-800">
        <h3 className="font-medium text-lg mb-2">Autenticazione richiesta</h3>
        <p>È necessario effettuare l'accesso per visualizzare i lead.</p>
      </div>
    );
  }
  
  // Se in caricamento, mostra uno skeleton
  if (isLoading) {
    return (
      <div className="animate-pulse">
        <div className="h-10 bg-gray-200 rounded w-1/4 mb-6"></div>
        <div className="space-y-4">
          {[1, 2, 3, 4, 5].map(i => (
            <div key={i} className="h-16 bg-gray-200 rounded"></div>
          ))}
        </div>
      </div>
    );
  }
  
  // Se c'è un errore, mostralo
  if (error) {
    return (
      <div className="p-4 bg-red-50 rounded-lg border border-red-200 text-red-800">
        <h3 className="font-medium text-lg mb-2">Errore</h3>
        <p>{error}</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* Lista dei lead */}
      <div className="col-span-1 lg:col-span-1">
        <div className="mb-4 flex flex-col sm:flex-row gap-4">
          <div className="flex-1">
            <input
              type="text"
              placeholder="Cerca per azienda o email..."
              value={filterText}
              onChange={(e) => setFilterText(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500"
            />
          </div>
          
          <div>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500"
            >
              <option value="tutti">Tutti gli stati</option>
              <option value="qualificato">Qualificati</option>
              <option value="interessante">Interessanti</option>
              <option value="da approfondire">Da approfondire</option>
              <option value="convertito">Convertiti</option>
              <option value="non interessato">Non interessati</option>
            </select>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="bg-gray-50 px-4 py-3 border-b border-gray-200">
            <h3 className="font-medium text-gray-700">
              Lead Transizione 5.0 ({filteredLeads.length})
            </h3>
          </div>
          
          {filteredLeads.length === 0 ? (
            <div className="p-4 text-center text-gray-500">
              Nessun lead trovato con i filtri selezionati.
            </div>
          ) : (
            <div className="divide-y divide-gray-200 max-h-[70vh] overflow-y-auto">
              {filteredLeads.map(lead => (
                <div 
                  key={lead.id}
                  className={`p-4 hover:bg-gray-50 cursor-pointer ${selectedLeadId === lead.id ? 'bg-gray-50' : ''}`}
                  onClick={() => setSelectedLeadId(lead.id)}
                >
                  <div className="flex justify-between items-start">
                    <div>
                      <div className="font-medium">{lead.azienda || 'Azienda non specificata'}</div>
                      <div className="text-sm text-gray-500">{lead.email || 'Email non specificata'}</div>
                    </div>
                    <div className="flex flex-col items-end">
                      <span className={`px-2 py-1 rounded-full text-xs ${getStatusColor(lead.stato)}`}>
                        {lead.stato}
                      </span>
                      <div className="text-xs text-gray-500 mt-1">
                        {lead.data_creazione ? formatDate(lead.data_creazione) : ''}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
      
      {/* Dettagli del lead */}
      <div className="col-span-1 lg:col-span-2">
        {selectedLeadId ? (
          isDetailLoading ? (
            <div className="animate-pulse">
              <div className="h-8 bg-gray-200 rounded w-1/3 mb-4"></div>
              <div className="space-y-4">
                {[1, 2, 3, 4, 5].map(i => (
                  <div key={i} className="h-12 bg-gray-200 rounded"></div>
                ))}
              </div>
            </div>
          ) : (
            selectedLead ? (
              <div className="bg-white rounded-lg shadow overflow-hidden">
                <div className="bg-gray-50 px-4 py-3 border-b border-gray-200 flex justify-between items-center">
                  <h3 className="font-medium text-gray-700">
                    Dettagli lead: {selectedLead.azienda_data.nome_azienda || 'Azienda non specificata'}
                  </h3>
                  <div className="flex gap-2">
                    <select
                      value={selectedLead.stato}
                      onChange={(e) => updateLeadStatus(selectedLead.id, e.target.value)}
                      className={`text-xs px-2 py-1 rounded-full border-none ${getStatusColor(selectedLead.stato)}`}
                    >
                      <option value="qualificato">Qualificato</option>
                      <option value="interessante">Interessante</option>
                      <option value="da approfondire">Da approfondire</option>
                      <option value="convertito">Convertito</option>
                      <option value="non interessato">Non interessato</option>
                    </select>
                  </div>
                </div>
                
                <div className="p-4 grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* Dati azienda */}
                  <div className="space-y-4">
                    <h4 className="font-medium text-gray-700 border-b pb-2">Informazioni azienda</h4>
                    
                    <div>
                      <div className="text-sm text-gray-500">Nome azienda</div>
                      <div>{selectedLead.azienda_data.nome_azienda || 'Non specificato'}</div>
                    </div>
                    
                    <div>
                      <div className="text-sm text-gray-500">Dimensione</div>
                      <div>{selectedLead.azienda_data.dimensione || 'Non specificato'}</div>
                    </div>
                    
                    <div>
                      <div className="text-sm text-gray-500">Settore</div>
                      <div>{selectedLead.azienda_data.settore || 'Non specificato'}</div>
                    </div>
                    
                    <div>
                      <div className="text-sm text-gray-500">Regione</div>
                      <div>{selectedLead.azienda_data.regione || 'Non specificato'}</div>
                    </div>
                  </div>
                  
                  {/* Dati contatto */}
                  <div className="space-y-4">
                    <h4 className="font-medium text-gray-700 border-b pb-2">Informazioni contatto</h4>
                    
                    <div>
                      <div className="text-sm text-gray-500">Nome e cognome</div>
                      <div>
                        {selectedLead.contatto_data.nome || ''} {selectedLead.contatto_data.cognome || ''}
                        {!selectedLead.contatto_data.nome && !selectedLead.contatto_data.cognome && 'Non specificato'}
                      </div>
                    </div>
                    
                    <div>
                      <div className="text-sm text-gray-500">Ruolo</div>
                      <div>{selectedLead.contatto_data.ruolo || 'Non specificato'}</div>
                    </div>
                    
                    <div>
                      <div className="text-sm text-gray-500">Email</div>
                      <div>{selectedLead.contatto_data.email || 'Non specificato'}</div>
                    </div>
                    
                    <div>
                      <div className="text-sm text-gray-500">Telefono</div>
                      <div>{selectedLead.contatto_data.telefono || 'Non specificato'}</div>
                    </div>
                  </div>
                  
                  {/* Dati investimento */}
                  <div className="space-y-4 md:col-span-2">
                    <h4 className="font-medium text-gray-700 border-b pb-2">Informazioni investimento</h4>
                    
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div>
                        <div className="text-sm text-gray-500">Tipo investimento</div>
                        <div>{selectedLead.investimenti_data.tipo_investimento || 'Non specificato'}</div>
                      </div>
                      
                      <div>
                        <div className="text-sm text-gray-500">Budget</div>
                        <div>{selectedLead.investimenti_data.budget || 'Non specificato'}</div>
                      </div>
                      
                      <div>
                        <div className="text-sm text-gray-500">Tempistiche</div>
                        <div>{selectedLead.investimenti_data.tempistiche || 'Non specificato'}</div>
                      </div>
                    </div>
                    
                    {selectedLead.investimenti_data.descrizione_progetto && (
                      <div>
                        <div className="text-sm text-gray-500">Descrizione progetto</div>
                        <div className="bg-gray-50 p-3 rounded-lg text-sm">
                          {selectedLead.investimenti_data.descrizione_progetto}
                        </div>
                      </div>
                    )}
                  </div>
                  
                  {/* Metadati e note */}
                  <div className="md:col-span-2 space-y-4">
                    <h4 className="font-medium text-gray-700 border-b pb-2">Metadati e note</h4>
                    
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                      <div>
                        <div className="text-sm text-gray-500">Score</div>
                        <div className="font-medium text-xl">{selectedLead.score}</div>
                      </div>
                      
                      <div>
                        <div className="text-sm text-gray-500">Data creazione</div>
                        <div>{formatDate(selectedLead.data_creazione)}</div>
                      </div>
                      
                      <div>
                        <div className="text-sm text-gray-500">Fonte</div>
                        <div>{selectedLead.fonte}</div>
                      </div>
                      
                      <div>
                        <div className="text-sm text-gray-500">Assegnato a</div>
                        <div>{selectedLead.assegnato_a || 'Non assegnato'}</div>
                      </div>
                    </div>
                    
                    <div>
                      <div className="text-sm text-gray-500 flex justify-between items-center">
                        <span>Note</span>
                        <button
                          onClick={() => setIsEditingNote(!isEditingNote)}
                          className="text-xs text-blue-600 hover:underline"
                        >
                          {isEditingNote ? 'Annulla' : 'Modifica'}
                        </button>
                      </div>
                      
                      {isEditingNote ? (
                        <div className="mt-2">
                          <textarea 
                            value={noteText}
                            onChange={(e) => setNoteText(e.target.value)}
                            className="w-full p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 min-h-24"
                          />
                          <div className="flex justify-end mt-2">
                            <button
                              // Qui andrebbe implementata la funzione per salvare le note
                              className="px-3 py-1 bg-emerald-600 text-white rounded-lg text-sm hover:bg-emerald-700"
                            >
                              Salva note
                            </button>
                          </div>
                        </div>
                      ) : (
                        <div className="bg-gray-50 p-3 rounded-lg text-sm min-h-24">
                          {selectedLead.note || 'Nessuna nota.'}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <div className="p-4 bg-yellow-50 rounded-lg border border-yellow-200 text-yellow-800">
                <h3 className="font-medium text-lg mb-2">Lead non trovato</h3>
                <p>Il lead selezionato non è disponibile o è stato eliminato.</p>
              </div>
            )
          )
        ) : (
          <div className="p-4 bg-blue-50 rounded-lg border border-blue-200 text-blue-800">
            <h3 className="font-medium text-lg mb-2">Nessun lead selezionato</h3>
            <p>Seleziona un lead dalla lista per visualizzarne i dettagli.</p>
          </div>
        )}
      </div>
    </div>
  );
}