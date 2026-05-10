def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])

    obstacles = observation.get("obstacles", []) or []
    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def ok(x, y): return inb(x, y) and (x, y) not in blocked
    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2); dy = abs(y1 - y2)
        return dx if dx > dy else dy

    role = (observation.get("self_role") or "").lower()
    i_am_evader = ("evad" in role) or ("runner" in role) or ("escape" in role) or ("hide" in role)

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    if i_am_evader:
        tx, ty = max(corners, key=lambda c: (cheb(c[0], c[1], ox, oy), c[0] + c[1]))
    else:
        tx, ty = ox, oy

    best = None  # (score, dx, dy)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        d_op = cheb(nx, ny, ox, oy)
        d_goal = cheb(nx, ny, tx, ty)

        # Obstacle avoidance: prefer positions with fewer blocked neighbors (local).
        neigh_blocked = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                px, py = nx + ax, ny + ay
                if (px, py) in blocked:
                    neigh_blocked += 1

        if i_am_evader:
            # Maximize distance from pursuer; then move toward far corner; avoid clutter near obstacles.
            score = (d_op * 10_000) + (d_goal * 10) - (neigh_blocked * 50)
            if best is None or score > best[0]:
                best = (score, dx, dy)
        else:
            # Minimize distance to opponent; tie-break by aligning with relative x/y ("wall runner").
            relx = 0 if nx == ox else (1 if nx > ox else -1)
            rely = 0 if ny == oy else (1 if ny > oy else -1)
            align = (1 if (dx == relx or dy == rely) else 0)
            score = (-d_op * 10_000) + (-d_goal * 10) + (align * 200) - (neigh_blocked * 50)
            if best is None or score > best[0]:
                best = (score, dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[1]), int(best[2])]