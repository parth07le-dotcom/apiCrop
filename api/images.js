
import { list } from '@vercel/blob';

export const config = {
    runtime: 'nodejs',
};

export default async function handler(request, response) {
    try {
        const { blobs } = await list();

        // Transform to unified format: { url, pathname, uploadedAt }
        const assets = {};

        blobs.forEach(blob => {
            let category = 'Uploaded';
            let name = blob.pathname;

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

        response.status(200).json(assets);
    } catch (error) {
        response.status(500).json({ error: error.message });
    }
}
