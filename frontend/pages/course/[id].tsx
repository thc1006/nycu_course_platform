import { useRouter } from 'next/router';
import useSWR from 'swr';
import axios from 'axios';

const fetcher = (url: string) => axios.get(url).then((res) => res.data);

export default function CourseDetail() {
  const router = useRouter();
  const { id } = router.query;

  const { data: course, error } = useSWR(
    id ? `/api/courses/${id}` : null,
    fetcher
  );

  if (error) return <div className="p-6">Failed to load course.</div>;
  if (!course) return <div className="p-6">Loading…</div>;

  return (
    <div className="p-6 max-w-3xl mx-auto">
      <h1 className="text-2xl font-bold mb-2">{course.name}</h1>
      <p className="text-sm text-gray-700 mb-4">{course.crs_no} {course.teacher ? `· ${course.teacher}` : ''}</p>
      {course.credits && (
        <p className="mb-4">Credits: {course.credits}</p>
      )}
      {course.details && (
        <div>
          <h2 className="text-xl font-semibold mb-2">Course Details</h2>
          {/* The details field contains a JSON string with additional fields.  */}
          <pre className="whitespace-pre-wrap bg-gray-50 p-4 rounded shadow">
            {JSON.stringify(JSON.parse(course.details), null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
}