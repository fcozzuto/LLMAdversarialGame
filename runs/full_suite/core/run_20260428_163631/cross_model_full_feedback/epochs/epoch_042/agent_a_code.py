def choose_move(observation):
    w = int(observation.get("grid_width", 8)); h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    obst = set()
    for p in observation.get("obstacles", []) or []:
        try:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obst.add((x, y))
        except: pass

    resources = []
    for r in observation.get("resources", []) or []:
        try:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obst:
                resources.append((x, y))
        except: pass

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obst:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    def man(a, b): return abs(a[0]-b[0]) + abs(a[1]-b[1])

    # Prefer moves that secure "contested" resources: we are closer (or will be).
    # Add mild pressure to reduce opponent's access to those same resources.
    best_move = (0, 0)
    best_score = -10**18

    center = (w//2, h//2)
    for dx, dy, nx, ny in legal:
        my_pos = (nx, ny)
        opp_pos = (ox, oy)
        score = 0
        if resources:
            for rx, ry in resources:
                d_my = man(my_pos, (rx, ry))
                d_op = man(opp_pos, (rx, ry))
                # Securing advantage
                if d_my < d_op:
                    score += 1200 - 40*d_my
                elif d_my == d_op:
                    score += 500 - 30*d_my
                else:
                    # If opponent is closer, try to reduce their edge.
                    score += (d_my - d_op) * 10
                # Also give a small reward for nearing any resource
                score += max(0, 60 - 8*d_my)
        # Threaten by moving toward center (helps future reach) if no resources
        score += -man(my_pos, center) * 3
        # Tiny determinism tie-break: closer to opponent reduces "distance advantage"
        score += -man(my_pos, opp_pos)

        if score > best_score:
            best_score = score
            best_move = (dx, dy)
        elif score == best_score:
            # deterministic tie-break: prioritize non-stay, then smallest dx, then smallest dy
            if best_move == (0, 0) and (dx, dy) != (0, 0):
                best_move = (dx, dy)
            elif (dx, dy) != (0, 0) and (dx, dy) < best_move:
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]