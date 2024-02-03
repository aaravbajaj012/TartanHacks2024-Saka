import LoadingIcons from 'react-loading-icons';
import LoadingIcon from './loadingIcon';

export default function Loading() {
  return (
    <div className="w-full h-full flex items-center justify-center">
      <LoadingIcon borderColor="border-slate-400" width="w-14"/>
    </div>
  );
}

