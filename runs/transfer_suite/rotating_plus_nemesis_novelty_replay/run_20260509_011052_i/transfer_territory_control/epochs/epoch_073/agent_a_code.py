def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (sx, sy))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        try:
            obs.add((int(p[0]), int(p[1])))
        except:
            pass

    T = set()
    for key in ("resources", "unclaimed_cells", "unclaimed"):
        lst = observation.get(key) or []
        for p in lst:
            try:
                T.add((int(p[0]), int(p[1])))
            except:
                pass

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    cand = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best = None
    best_score = None

    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obs:
            continue

        dop = md(nx, ny, ox, oy)
        if (nx, ny) in T:
            score = 10_000 + dop
        elif T:
            dt = None
            for tx, ty in T:
                v = md(nx, ny, tx, ty)
                if dt is None or v < dt:
                    dt = v
            score = 2000 - dt * 10 + dop
        else:
            score = dop

        if best is None or score > best_score:
            best = [dx, dy]
            best_score = score

    if best is not None:
        return best

    # fallback: stay if possible else first in-bounds non-obstacle
    if inb(sx, sy) and (sx, sy) not in obs:
        return [0, 0]
    for dx, dy in cand[:-1]:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obs:
            return [dx, dy]
    return [0, 0]