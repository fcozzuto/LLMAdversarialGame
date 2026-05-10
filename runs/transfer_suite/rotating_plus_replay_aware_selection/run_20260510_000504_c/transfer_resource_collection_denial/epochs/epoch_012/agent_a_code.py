def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])[:2]
    ox, oy = observation.get("opponent_position", [0, 0])[:2]

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

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

    res = [p for p in parse_resources() if p not in obstacles]
    inb = lambda x, y: 0 <= x < w and 0 <= y < h

    if not res:
        dx = 0 if sx == ox else (1 if ox > sx else -1)
        dy = 0 if sy == oy else (1 if oy > sy else -1)
        if not inb(sx + dx, sy + dy) or (sx + dx, sy + dy) in obstacles:
            dx, dy = 0, 0
        return [dx, dy]

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best = None
    best_val = -10**9
    for rx, ry in res:
        d_me = md(sx, sy, rx, ry)
        d_op = md(ox, oy, rx, ry)
        if d_me == 0:
            best = (rx, ry)
            break
        # Prefer resources we can reach first; also prefer being closer overall.
        val = (d_op - d_me) * 10 - d_me
        if best is None or val > best_val:
            best_val = val
            best = (rx, ry)

    tx, ty = best
    step_cands = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    chosen = (0, 0)
    chosen_val = -10**9
    for dx, dy in step_cands:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        # Main objective: reduce distance to target; secondary: deny opponent by increasing their distance to target.
        v = -(md(nx, ny, tx, ty)) * 3 + (md(ox, oy, tx, ty) - md(ox, oy, tx, ty)) * 0
        # Secondary: keep away from opponent while advancing.
        v += md(nx, ny, ox, oy) * 0.05
        # Tertiary deterministic tiebreaker: prefer moves toward target axis, then diagonals.
        if md(nx, ny, tx, ty) < md(sx, sy, tx, ty):
            v += 0.1
        if chosen is None or v > chosen_val:
            chosen_val = v
            chosen = (dx, dy)

    return [int(chosen[0]), int(chosen[1])]