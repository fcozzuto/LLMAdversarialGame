def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    self_role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    self_ev = ("evad" in self_role) or ("run" in self_role) or ("escap" in self_role)
    opp_ev = ("evad" in opp_role) or ("run" in opp_role) or ("escap" in opp_role)
    pursuer = (not self_ev) or opp_ev

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best = None
    best_val = None
    oppx, oppy = ox, oy

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        if not pursuer and nx == oppx and ny == oppy:
            continue

        d1 = cheb(nx, ny, oppx, oppy)

        # Simple 2-step lookahead for evasion: prefer moves that keep distance after opponent responds greedily.
        if not pursuer:
            # Assume opponent moves greedily to reduce distance, without stepping into obstacles.
            nd = d1
            for odx, ody in dirs:
                enx, eny = oppx + odx, oppy + ody
                if enx < 0 or enx >= w or eny < 0 or eny >= h:
                    continue
                if (enx, eny) in obstacles:
                    continue
                if enx == nx and eny == ny:
                    nd = 0
                    break
                dd = cheb(enx, eny, nx, ny)
                if dd < nd:
                    nd = dd
            val = nd
        else:
            val = -d1  # minimize distance => maximize negative distance

        if best is None or (pursuer and val > best_val) or ((not pursuer) and val > best_val):
            best_val = val
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best