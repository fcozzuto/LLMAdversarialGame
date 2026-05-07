def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    best_rx, best_ry = resources[0]
    best_key = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Prefer targets we can reach earlier and that opponent is slower on; tie-break by closer.
        key = (do - ds, -ds, -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best_rx, best_ry = rx, ry

    tx, ty = best_rx, best_ry

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                d = cheb(nx, ny, tx, ty)
                # Small bias to keep progressing: prefer decreasing distance to target and increasing y if tied.
                score = (-d, -(ny - sy), -abs(nx - tx), -abs(ny - ty))
                # If landing on a resource, strongly prefer it.
                if (nx, ny) in resources:
                    score = (1, 0, 0, 0)
                moves.append((score, dx, dy))
    moves.sort(key=lambda t: t[0], reverse=True)
    return [int(moves[0][1]), int(moves[0][2])]