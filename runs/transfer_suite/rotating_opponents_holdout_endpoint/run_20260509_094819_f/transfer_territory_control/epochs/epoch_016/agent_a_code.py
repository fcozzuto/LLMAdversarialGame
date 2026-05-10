def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    unclaimed = observation.get("unclaimed_cells") or []
    if isinstance(unclaimed, dict):
        unclaimed = list(unclaimed.keys())

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_score = -10**18

    if unclaimed:
        targets = []
        for p in unclaimed:
            if not isinstance(p, (list, tuple)) or len(p) < 2:
                continue
            tx, ty = int(p[0]), int(p[1])
            if (tx, ty) in obstacles or not inb(tx, ty):
                continue
            targets.append((tx, ty))
        if targets:
            for dx, dy in moves:
                nx, ny = sx + dx, sy + dy
                if not inb(nx, ny) or (nx, ny) in obstacles:
                    continue
                best_tdist = 10**9
                best_odist = -10**9
                for tx, ty in targets:
                    d = abs(tx - nx) + abs(ty - ny)
                    if d < best_tdist:
                        best_tdist = d
                    do = abs(tx - ox) + abs(ty - oy)
                    if do > best_odist:
                        best_odist = do
                score = -best_tdist + 0.1 * best_odist
                if score > best_score:
                    best_score = score
                    best = [dx, dy]
            if best is not None:
                return best

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        score = abs(nx - ox) + abs(ny - oy)
        if score > best_score:
            best_score = score
            best = [dx, dy]
    if best is None:
        return [0, 0]
    return best