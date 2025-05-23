// components/sections/BenefitsTable.tsx
import React from 'react';

interface BenefitsTableProps {
  // Dati potrebbero essere passati come props in futuro
}

export default function BenefitsTable({}: BenefitsTableProps) {
  return (
    <section className="mb-12">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">Percentuali di credito d'imposta</h2>
      <div className="overflow-x-auto">
        <table className="min-w-full bg-white rounded-lg shadow-md">
          <thead className="bg-emerald-50">
            <tr>
              <th className="px-6 py-3 text-left text-sm font-medium text-gray-700 uppercase tracking-wider">
                Tipologia investimento
              </th>
              <th className="px-6 py-3 text-left text-sm font-medium text-gray-700 uppercase tracking-wider">
                Credito d'imposta
              </th>
              <th className="px-6 py-3 text-left text-sm font-medium text-gray-700 uppercase tracking-wider">
                Requisiti
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            <tr>
              <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-800">
                Beni materiali 4.0
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-emerald-600 font-semibold">
                35% - 45%
              </td>
              <td className="px-6 py-4 text-sm text-gray-600">
                Riduzione consumi energetici almeno 3% (35%) o 5% (45%)
              </td>
            </tr>
            <tr>
              <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-800">
                Beni immateriali 4.0
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-emerald-600 font-semibold">
                35%
              </td>
              <td className="px-6 py-4 text-sm text-gray-600">
                Software, sistemi, piattaforme per i beni materiali 4.0
              </td>
            </tr>
            <tr>
              <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-800">
                Formazione 4.0
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-emerald-600 font-semibold">
                40%
              </td>
              <td className="px-6 py-4 text-sm text-gray-600">
                Formazione su tecnologie 4.0 e transizione ecologica
              </td>
            </tr>
            <tr>
              <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-800">
                Energia rinnovabile
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-emerald-600 font-semibold">
                35% - 45%
              </td>
              <td className="px-6 py-4 text-sm text-gray-600">
                Impianti di autoconsumo per riduzione consumi
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  );
}