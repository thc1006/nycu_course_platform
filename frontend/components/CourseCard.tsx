import React from 'react';
import { Clock, MapPin, User, BookOpen, Plus, Check } from 'lucide-react';

interface CourseCardProps {
  id: number;
  crs_no: string;
  name: string;
  teacher: string;
  credits: number;
  time: string;
  classroom: string;
  dept?: string;
  acy?: number;
  sem?: number;
  onAddToSchedule?: (courseId: number) => void;
}

export const CourseCard: React.FC<CourseCardProps> = ({
  id,
  crs_no,
  name,
  teacher,
  credits,
  time,
  classroom,
  dept,
  acy,
  sem,
  onAddToSchedule,
}) => {
  const [isAdded, setIsAdded] = React.useState(false);
  const [isHovered, setIsHovered] = React.useState(false);

  const handleAddToSchedule = () => {
    if (!isAdded) {
      setIsAdded(true);
      onAddToSchedule?.(id);
      setTimeout(() => setIsAdded(false), 2000);
    }
  };

  const formatTime = (timeStr: string) => {
    if (!timeStr || timeStr === 'N/A') return 'Time not specified';
    return timeStr.length > 30 ? timeStr.substring(0, 30) + '...' : timeStr;
  };

  const formatClassroom = (room: string) => {
    if (!room || room === 'N/A') return 'Room TBA';
    return room.length > 20 ? room.substring(0, 20) + '...' : room;
  };

  return (
    <div
      className="group relative bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm hover:shadow-xl transition-all duration-300 overflow-hidden"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* Card Header with gradient */}
      <div className="relative h-2 bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500" />

      <div className="p-6 space-y-4">
        {/* Course Code and Credits */}
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-1">
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-300">
                {crs_no}
              </span>
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-300">
                {credits} Credits
              </span>
            </div>
            {dept && (
              <span className="text-xs text-gray-500 dark:text-gray-400">
                {dept}
              </span>
            )}
          </div>
        </div>

        {/* Course Name */}
        <div>
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white line-clamp-2 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors">
            {name}
          </h3>
        </div>

        {/* Course Details */}
        <div className="space-y-2">
          <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
            <User className="h-4 w-4 flex-shrink-0" />
            <span className="truncate">{teacher || 'Instructor TBA'}</span>
          </div>

          <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
            <Clock className="h-4 w-4 flex-shrink-0" />
            <span className="truncate">{formatTime(time)}</span>
          </div>

          <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
            <MapPin className="h-4 w-4 flex-shrink-0" />
            <span className="truncate">{formatClassroom(classroom)}</span>
          </div>
        </div>

        {/* Semester Info */}
        {acy && sem && (
          <div className="pt-2 border-t border-gray-100 dark:border-gray-700">
            <span className="text-xs text-gray-500 dark:text-gray-400">
              {acy} - Semester {sem}
            </span>
          </div>
        )}

        {/* Action Button */}
        <button
          onClick={handleAddToSchedule}
          disabled={isAdded}
          className={`
            w-full mt-4 flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg
            font-medium transition-all duration-200 transform
            ${isAdded
              ? 'bg-green-500 dark:bg-green-600 text-white hover:bg-green-600 dark:hover:bg-green-700'
              : 'bg-blue-500 dark:bg-blue-600 text-white hover:bg-blue-600 dark:hover:bg-blue-700 hover:scale-[1.02]'
            }
            focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 dark:focus:ring-offset-gray-800
            disabled:opacity-75 disabled:cursor-not-allowed
          `}
        >
          {isAdded ? (
            <>
              <Check className="h-4 w-4" />
              Added to Schedule
            </>
          ) : (
            <>
              <Plus className="h-4 w-4" />
              Add to Schedule
            </>
          )}
        </button>
      </div>

      {/* Hover Effect Overlay */}
      <div
        className={`
          absolute inset-0 bg-gradient-to-t from-blue-500/10 to-transparent
          opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none
        `}
      />
    </div>
  );
};