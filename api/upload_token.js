import { handleUpload } from '@vercel/blob/client';

export const config = {
    runtime: 'nodejs',
};

export default async function handler(request) {
    const body = await request.json();

    try {
        const jsonResponse = await handleUpload({
            body,
            request,
            onBeforeGenerateToken: async (pathname /*, clientPayload */) => {
                return {
                    allowedContentTypes: ['application/pdf', 'image/png', 'image/jpeg', 'image/jpg', 'application/x-pdf'],
                    tokenPayload: JSON.stringify({}),
                };
            },
            onUploadCompleted: async ({ blob, tokenPayload }) => {
                // console.log('blob uploaded', blob.url);
            },
        });

        return new Response(JSON.stringify(jsonResponse));
    } catch (error) {
        return new Response(
            JSON.stringify(
                { error: error.message }
            ),
            { status: 400, statusText: 'Bad Request' }
        );
    }
}
