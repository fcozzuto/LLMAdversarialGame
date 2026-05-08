def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
    resources = []
    for r in (observation.get("resources") or []):
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx + dy

    best = None
    best_key = None
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    pref = (-1, 0, 1)
    for dx in pref:
        for dy in pref:
            if (dx, dy) not in moves:
                continue
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            # Score by how well we beat opponent on the nearest resource from our next position.
            nearest_score = None
            for rx, ry in resources:
                ds = man(nx, ny, rx, ry)
                do = man(ox, oy, rx, ry)
                # Primary: minimize opponent advantage; Secondary: minimize our distance.
                key = (ds - do, ds, abs(rx - ox) + abs(ry - oy))
                if nearest_score is None or key < nearest_score:
                    nearest_score = key
            # Small deterministic bias to move away from obstacles? none needed; tie-break by dx,dy order.
            key2 = (nearest_score[0], nearest_score[1], nearest_score[2], dx, dy)
            if best_key is None or key2 < best_key:
                best_key = key2
                best = (dx, dy)

    return [int(best[0]) if best else 0, int(best[1]) if best else 0]