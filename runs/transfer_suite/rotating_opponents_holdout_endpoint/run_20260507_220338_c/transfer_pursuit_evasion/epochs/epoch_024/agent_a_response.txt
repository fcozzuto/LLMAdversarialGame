def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    self_role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    self_is_evader = "evad" in self_role
    opp_is_evader = "evad" in opp_role

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def ok(x, y): return inb(x, y) and (x, y) not in blocked
    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    # Opponent greedy policy (assume they are pursuer when not evader)
    def opp_next(px, py, tx, ty):
        best = (0, 0)
        bestv = -10**18 if opp_is_evader else 10**18
        for dx, dy in dirs:
            nx, ny = px + dx, py + dy
            if not ok(nx, ny):
                continue
            v = dist2(nx, ny, tx, ty)
            if opp_is_evader:
                if v > bestv:
                    bestv, best = v, (dx, dy)
            else:
                if v < bestv:
                    bestv, best = v, (dx, dy)
        return best

    candidates = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        # immediate objective: evader wants far, pursuer wants close
        d_self = dist2(nx, ny, ox, oy)
        immediate = -d_self if self_is_evader else d_self

        # 1-ply lookahead: evaluate resulting distance after opponent moves greedily
        odx, ody = opp_next(ox, oy, nx, ny)
        nox, noy = ox + odx, oy + ody
        d_after = dist2(nox, noy, nx, ny)

        # Capture radius is 0, so just keep d_after large for evader and small for pursuer
        if self_is_evader:
            score = d_after * 4 + d_self * 1 - (abs(dx) + abs(dy)) * 0.01
        else:
            score = -d_after * 4 - d_self * 1 - (abs(dx) + abs(dy)) * 0.01

        candidates.append((score, dx, dy))

    candidates.sort(reverse=True, key=lambda t: t[0])
    _, dx, dy = candidates[0] if candidates else (0, 0, 0)
    return [int(dx), int(dy)]