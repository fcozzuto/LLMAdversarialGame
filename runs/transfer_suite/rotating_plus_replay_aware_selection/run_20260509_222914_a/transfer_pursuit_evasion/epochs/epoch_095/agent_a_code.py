def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = (observation.get("self_role") or "").lower()
    is_evader = ("evader" in role) or ("runner" in role) or ("escape" in role) or ("fugitive" in role)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def obst_adj(nx, ny):
        c = 0
        for dx, dy in moves:
            if dx == 0 and dy == 0:
                continue
            px, py = nx + dx, ny + dy
            if not (0 <= px < w and 0 <= py < h) or (px, py) in obstacles:
                c += 1
        return c

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    far_corner = max(corners, key=lambda c: man(c[0], c[1], ox, oy))

    best = None
    best_sc = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        d = man(nx, ny, ox, oy)
        ao = obst_adj(nx, ny)

        if is_evader:
            # Prefer maximizing distance, and also bias toward the farthest corner, while avoiding tight obstacle-adjacent tiles.
            corner_bias = man(nx, ny, far_corner[0], far_corner[1])
            sc = (d * 20) - (corner_bias * 0.12) - (ao * 1.1)
        else:
            # Prefer minimizing distance; add small bias to keep moving in a consistent direction away from obstacles.
            sc = (-d * 20) - (ao * 0.7) + (man(nx, ny, sx, sy) * 0.02)

        if best_sc is None or sc > best_sc:
            best_sc = sc
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [best[0], best[1]]