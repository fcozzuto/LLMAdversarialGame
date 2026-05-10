def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    role = str(observation.get("self_role", "")).lower()
    we_evader = ("evader" in role) or ("runner" in role)

    obstacles = observation.get("obstacles", []) or []
    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy
    def adj_obst(x, y):
        c = 0
        for i in (-1, 0, 1):
            for j in (-1, 0, 1):
                if (x + i, y + j) in blocked: c += 1
        return c

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    target_corner = max(corners, key=lambda c: cheb(c[0], c[1], ox, oy))

    best = (None, -10**9)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny): nx, ny = sx, sy
        if (nx, ny) in blocked: nx, ny = sx, sy
        d = cheb(nx, ny, ox, oy)
        wall = min(nx, w - 1 - nx) + min(ny, h - 1 - ny)
        ao = adj_obst(nx, ny)

        if we_evader:
            # Farthest-from-opponent with bias to slide toward a specific far corner; avoid obstacle-adjacent traps.
            tx, ty = target_corner
            to_corner = cheb(nx, ny, tx, ty)
            score = (d * 10) - (to_corner * 2) + (wall * 0.2) - (ao * 2.5)
            # keep deterministic tie-break toward larger dx,dy ordering
        else:
            # Pursue by minimizing distance; prefer routes away from obstacles/walls.
            score = (-d * 12) + (wall * 0.15) - (ao * 3.0)

        key = (score, dx, dy)
        if key > best[1:]:
            best = ((dx, dy), score)

    return [int(best[0][0]), int(best[0][1])]