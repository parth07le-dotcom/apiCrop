
import { list } from '@vercel/blob';

export const config = {
    runtime: 'nodejs',
};

export default async function handler(request) {
    try {
        const { blobs } = await list();

        // Transform to unified format: { url, pathname, uploadedAt }
        // We want to group them or just return a flat list?
        // The current gallery.html expects { "category": ["filename", ...] }
        // BUT we want to move to: { "category": [{ url: "...", name: "..." }] }

        // For Vercel Blob, "pathname" is like "logos/jobid_filename".
        // We can group by folder if we want.

        const assets = {};

        blobs.forEach(blob => {
            // blob.pathname looks like "logos/file.png" or just "file.png"
            // Let's use a "Vercel Storage" category for all of them, 
            // OR try to extract a category from the path.

            let category = 'Uploaded';
            let name = blob.pathname;

            // Simple heuristic: if path has slashes, use first part as category
            if (blob.pathname.includes('/')) {
                const parts = blob.pathname.split('/');
                category = parts[0];
                name = parts.slice(1).join('/');
            }

            if (!assets[category]) assets[category] = [];

            assets[category].push({
                name: name,
                url: blob.url,
                date: blob.uploadedAt
            });
        });

        return new Response(JSON.stringify(assets), {
            status: 200,
            headers: {
                'content-type': 'application/json',
                'cache-control': 'public, max-age=60' // Cache for 60 seconds
            },
        });
    } catch (error) {
        return new Response(JSON.stringify({ error: error.message }), {
            status: 500,
        });
    }
}
