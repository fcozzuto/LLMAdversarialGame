def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def dist(a, b): return max(abs(a[0] - b[0]), abs(a[1] - b[1]))
    def cand_score(cx, cy):
        best = -10**18
        for r in resources:
            if not r or len(r) < 2: 
                continue
            rx, ry = int(r[0]), int(r[1])
            if not inb(rx, ry) or (rx, ry) in obs:
                continue
            ds = dist((cx, cy), (rx, ry))
            do = dist((ox, oy), (rx, ry))
            # Prefer resources we reach earlier than opponent; slight tie-break for closer
            s = (do - ds) * 10 - ds
            if s > best:
                best = s
        if best == -10**18:
            return -dist((cx, cy), (ox, oy))
        return best

    best_move = [0, 0]
    best_val = -10**18

    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                val = -10**18
            elif (nx, ny) in obs:
                val = -10**18
            else:
                val = cand_score(nx, ny)
                # If moving adjacent to opponent, avoid (helps vs denier focus)
                if dist((nx, ny), (ox, oy)) <= 1:
                    val -= 5
                # If we can step onto a visible resource, strongly prefer
                for r in resources:
                    if r and len(r) >= 2 and int(r[0]) == nx and int(r[1]) == ny:
                        val += 1000
                        break
            if val > best_val:
                best_val = val
                best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]