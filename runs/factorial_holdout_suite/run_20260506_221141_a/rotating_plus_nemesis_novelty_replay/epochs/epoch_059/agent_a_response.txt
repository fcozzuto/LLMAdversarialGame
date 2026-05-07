def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    gw = int(observation.get("grid_width", 8) or 8)
    gh = int(observation.get("grid_height", 8) or 8)

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    obs_set = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            px, py = int(p[0]), int(p[1])
            if inb(px, py):
                obs_set.add((px, py))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if inb(rx, ry) and (rx, ry) not in obs_set:
                resources.append((rx, ry))
    if not resources:
        cx, cy = (gw - 1) // 2, (gh - 1) // 2
        dx = 0 if sx == cx else (1 if cx > sx else -1)
        dy = 0 if sy == cy else (1 if cy > sy else -1)
        return [dx, dy]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None  # (score, tx, ty, dx, dy)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs_set:
            continue

        best_res = -10**9
        best_t = resources[0]
        min_self = 10**9
        min_opp = 10**9
        for tx, ty in resources:
            sd = cheb(nx, ny, tx, ty)
            od = cheb(ox, oy, tx, ty)
            adv = od - sd  # positive means we are closer (or can arrive sooner)
            # favor resources we can beat opponent on; tie-break by sooner self arrival and larger separation
            val = adv * 10 - sd
            if adv < 0:
                val -= 5  # discourage chasing behind, unless it is very close
            if sd < min_self: min_self = sd
            if od < min_opp: min_opp = od
            if val > best_res or (val == best_res and (sd < cheb(sx, sy, best_t[0], best_t[1]))):
                best_res = val
                best_t = (tx, ty)

        # small bias: if we can capture something this turn (sd==0), strongly prioritize
        sd_cap = cheb(nx, ny, best_t[0], best_t[1])
        score = best_res + (1000 if sd_cap == 0 else 0) + (3 if min_self < min_opp else -1)

        cand = (score, best_t[0], best_t[1], dx, dy)
        if best is None or cand > best:
            best = cand

    if best is None:
        return [0, 0]
    return [best[3], best[4]]