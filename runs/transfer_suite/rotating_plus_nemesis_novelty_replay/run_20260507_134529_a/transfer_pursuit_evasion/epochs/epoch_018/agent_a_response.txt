def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    obs = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def neighbors_free(x, y):
        c = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if inb(x + ax, y + ay):
                    c += 1
        return c

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    role = observation.get("self_role", "pursuer") or "pursuer"
    pursuer = (role != "evader")

    # Heuristic "intercept": focus on reducing the dominant component and keep mobility.
    vx = 0
    vy = 0
    if ox != sx:
        vx = 1 if ox > sx else -1
    if oy != sy:
        vy = 1 if oy > sy else -1
    if abs(ox - sx) == 0:
        vx = 0
    if abs(oy - sy) == 0:
        vy = 0
    # Project where zigzag tends to go: alternating by component; simplest bounded projection.
    px = ox + (1 if vx != 0 else 0) * vx
    py = oy + (1 if vy != 0 else 0) * vy
    if not (0 <= px < w and 0 <= py < h) or (px, py) in obs:
        px, py = ox, oy

    best = None
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d_now = cheb(nx, ny, ox, oy)
        d_proj = cheb(nx, ny, px, py)

        # Primary: approach (or evade) projected position, then current.
        # Secondary: keep options (pursuer) or reduce opponent options (evader).
        mob = neighbors_free(nx, ny)
        center = abs((w - 1) * 0.5 - nx) + abs((h - 1) * 0.5 - ny)

        if pursuer:
            key = (d_proj, d_now, -mob, center)
        else:
            key = (-d_proj, -d_now, mob, -center)

        if best is None or key < best:
            best = key
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]