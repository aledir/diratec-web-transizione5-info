export function throttle(callback: Function, limit: number = 100) {
  let inThrottle: boolean = false;
  
  return function(this: any, ...args: any[]) {
    if (!inThrottle) {
      callback.apply(this, args);
      inThrottle = true;
      setTimeout(() => {
        inThrottle = false;
      }, limit);
    }
  };
}
