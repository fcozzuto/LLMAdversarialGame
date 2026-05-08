def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x, y):
        dx = x - ox
        if dx < 0: dx = -dx
        dy = y - oy
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    self_role = (observation.get("self_role") or "")
    pursuer = ("pursuer" in self_role.lower()) or (self_role.lower() == "pursuer")
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    best_sc = None
    best_mv = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        dist = cheb(nx, ny)
        # mobility around next position
        mob = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                tx, ty = nx + ax, ny + ay
                if inb(tx, ty):
                    mob += 1
        # obstacle threat: prefer not to step into dead-ends
        sc_mob = mob
        if pursuer:
            sc = (-dist * 1000) + (sc_mob * 3) - (1 if (nx, ny) == (ox, oy) else 0) * 0
        else:
            sc = (dist * 1000) + (sc_mob * 2)
            # discourage edging into own tightness when opponent is close
            if dist <= 1:
                sc -= 2 * (8 - sc_mob)
        if best_sc is None or sc > best_sc:
            best_sc = sc
            best_mv = (dx, dy)

    return [int(best_mv[0]), int(best_mv[1])]