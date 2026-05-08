def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = (10**9, None)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        dist = abs(nx - ox) + abs(ny - oy)
        adj_obs = 0
        if dist > 0:
            for ex in (-1, 0, 1):
                for ey in (-1, 0, 1):
                    if ex == 0 and ey == 0:
                        continue
                    ax, ay = nx + ex, ny + ey
                    if inb(ax, ay) and (ax, ay) in obs:
                        adj_obs += 1
        score = dist * 10 + adj_obs
        if score < best[0]:
            best = (score, [dx, dy])
    return best[1] if best[1] is not None else [0, 0]