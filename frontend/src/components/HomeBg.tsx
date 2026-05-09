import { useRef, useEffect } from "react";

export default function HomeBackground() {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const solLogo = new Image();
    solLogo.src = "https://cryptologos.cc/logos/solana-sol-logo.png";

    const particles: Particle[] = [];
    const PARTICLE_COUNT = 50;

    function resize() {
      if (!canvas) return;
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    }

    resize();
    window.addEventListener("resize", resize);

    class Particle {
      x!: number;
      y!: number;
      size!: number;
      speed!: number;
      opacity!: number;

      constructor() {
        this.reset();
      }

      reset(initial = false) {
        if (!canvas) return;
        this.x = Math.random() * canvas.width;
        this.y = initial ? Math.random() * canvas.height : canvas.height + Math.random() * 100;
        this.size = Math.random() * 15 + 10;
        this.speed = Math.random() * 0.4 + 0.2;
        this.opacity = Math.random() * 0.5 + 0.1; 
      }

      update() {
        this.y -= this.speed;
        if (this.y < -20) {
          this.reset();
        }

      }


      draw(context: CanvasRenderingContext2D) {
        context.globalAlpha = this.opacity;
        context.drawImage(solLogo, this.x, this.y, this.size, this.size);
        context.globalAlpha = 1.0;
      }

    }

    solLogo.onload = () => {
      for (let i = 0; i < PARTICLE_COUNT; i++) {
        particles.push(new Particle());
      }
    }

      let animationFrameId: number;

      function animate() {
        if (!ctx || !canvas) return;
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        particles.forEach((p) => {
          p.update();
          p.draw(ctx);
        });

        animationFrameId = requestAnimationFrame(animate);
      }

      animate();

      return () => {
        cancelAnimationFrame(animationFrameId);
      };
    }, []);

  return (
    <canvas
      ref={canvasRef}
      className="absolute inset-0 z-0 pointer-events-none opacity-100"
    />
  );
}