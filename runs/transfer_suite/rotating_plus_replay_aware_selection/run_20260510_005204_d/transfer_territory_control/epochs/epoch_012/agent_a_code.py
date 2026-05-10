def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        try:
            obs.add((int(p[0]), int(p[1])))
        except Exception:
            pass

    resources = observation.get("resources") or []
    res = []
    for p in resources:
        try:
            res.append((int(p[0]), int(p[1])))
        except Exception:
            pass
    if not res:
        rem = observation.get("remaining_resource_count", 0)
        if rem and observation.get("resource_positions"):
            for p in observation.get("resource_positions") or []:
                try:
                    res.append((int(p[0]), int(p[1])))
                except Exception:
                    pass

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def mindist(x, y, pts):
        if not pts:
            return w + h
        best = 10**9
        for px, py in pts[:16]:
            d = abs(x - px) + abs(y - py)
            if d < best:
                best = d
        return best

    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = int(sx) + dx, int(sy) + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obs:
            continue
        if nx == int(ox) and ny == int(oy):
            continue

        d_opp = abs(nx - int(ox)) + abs(ny - int(oy))
        d_res = mindist(nx, ny, res)
        score = d_opp * 3 - d_res * 1

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]