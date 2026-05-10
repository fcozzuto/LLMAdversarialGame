def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])[:2]
    ox, oy = observation.get("opponent_position", [0, 0])[:2]
    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h
    def parse_resources():
        out = []
        for r in observation.get("resources", []) or []:
            if isinstance(r, (list, tuple)) and len(r) >= 2:
                out.append((int(r[0]), int(r[1])))
            elif isinstance(r, dict):
                pos = r.get("position", None)
                if isinstance(pos, (list, tuple)) and len(pos) >= 2:
                    out.append((int(pos[0]), int(pos[1])))
                elif "x" in r and "y" in r:
                    out.append((int(r["x"]), int(r["y"])))
        return out
    res = [t for t in parse_resources() if t not in obstacles]
    if not res:
        dx = 0 if sx == ox else (1 if ox > sx else -1)
        dy = 0 if sy == oy else (1 if oy > sy else -1)
        step = [(-dx), (-dy)]
        nx, ny = sx + step[0], sy + step[1]
        if inb(nx, ny) and (nx, ny) not in obstacles:
            return step
        return [0, 0]
    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
    opp_pos = (ox, oy)
    best = None
    best_key = None
    for t in res:
        sd = man((sx, sy), t)
        od = man(opp_pos, t)
        # Prefer resources opponent isn't close to, but still allow contest if we're very near.
        key = (sd - od, sd, od, t[0], t[1])
        if best_key is None or key < best_key:
            best_key = key
            best = t
    tx, ty = best
    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            dist = man((nx, ny), (tx, ty))
            # Slightly discourage stepping toward opponent while contesting.
            dist_opp = man((nx, ny), opp_pos)
            candidates.append((dist - 0.15 * dist_opp, dist, -(dx * (tx - sx) + dy * (ty - sy)), dx, dy))
    if candidates:
        candidates.sort()
        _, _, _, dx, dy = candidates[0]
        return [int(dx), int(dy)]
    return [0, 0]