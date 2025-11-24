import { useEffect, RefObject } from "react";

/**
 * Хук для автоматической прокрутки элемента вниз при изменении его содержимого.
 * @param ref Ref объекта DOM, который нужно прокручивать.
 * @param dependencies Массив зависимостей, при изменении которых будет происходить прокрутка.
 */
export const useChatAutoScroll = <T extends HTMLElement>(
  ref: RefObject<T | null>,
  dependencies: any[]
) => {
  useEffect(() => {
    if (ref?.current) {
      ref.current.scrollTop = ref.current.scrollHeight;
    }
  }, dependencies);
};
