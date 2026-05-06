def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = observation.get("resources", []) or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                res.append((x, y))

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst
    def cheb(a, b):
        return max(abs(a[0]-b[0]), abs(a[1]-b[1]))
    def man(a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    # If stuck, make any legal move deterministically (lex by dx,dy order)
    if not inb(sx, sy):
        for dx, dy in moves:
            if inb(sx + dx, sy + dy):
                return [dx, dy]
        return [0, 0]

    # Opportunistic race/denial: prefer moves that let us reach resources earlier, and
    # slightly avoid positions where opponent is closer to the best resource.
    best_move = (0, 0)
    best_val = None
    center = (w // 2, h // 2)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        my_pos = (nx, ny)
        opp_pos = (nx - (sx - ox), ny - (sy - oy))  # just to reuse structure; not used
        base_center = -(abs(nx - center[0]) + abs(ny - center[1])) * 0.02
        if not res:
            val = base_center + man(my_pos, (ox, oy)) * 0.01
        else:
            # Evaluate best achievable resource advantage from this neighbor.
            local_best = -10**9
            for rx, ry in res:
                rpos = (rx, ry)
                my_d = cheb(my_pos, rpos)
                op_d = cheb((ox, oy), rpos)
                # Positive if we are closer (or tie-better); also add tie-break toward smaller my_d
                val_r = (op_d - my_d) * 1.0 - my_d * 0.05
                # Mild deny: if opponent is very close, discourage
                if op_d <= my_d:
                    val_r -= 0.12
                if val_r > local_best:
                    local_best = val_r
            val = local_best + base_center + (man((nx, ny), (ox, oy)) * 0.01)
        key = val
        if best_val is None or key > best_val or (key == best_val and (dx, dy) < best_move):
            best_val = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]