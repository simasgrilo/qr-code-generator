import Page from "./components/Page";

export default function Home() {
  return (
    <div className="font-sans items-center justify-items-center min-h-screen p-8 pb-20 gap-16 sm:p-20">
      <h1 className="font-normal py--10">QR Code Generator</h1>
      <main className="flex flex-col gap-[32px] row-start-1 items-center sm:items-start">
        <Page/>
      </main>
    </div>
  );
}
