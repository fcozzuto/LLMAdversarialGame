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
    pursuer = (not self_ev) or opp_ev  # if we are not evader, we pursue; else if opponent is evader, we pursue

    obs_set = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs_set.add((x, y))

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    corners = [(0,0),(0,h-1),(w-1,0),(w-1,h-1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best_score = None
    best_move = (0, 0)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs_set:
            continue

        d = cheb(nx, ny, ox, oy)
        dc = cheb(sx, sy, ox, oy)

        if pursuer:
            # primary: get closer (strictly prefer smaller distance)
            score = (1000 - d * 20) + (dc - d) * 50
            # slight preference to align toward opponent corner to reduce zig-zag
            far_corner = max(corners, key=lambda c: cheb(nx, ny, c[0], c[1]) - cheb(ox, oy, c[0], c[1]))
            score += (cheb(nx, ny, far_corner[0], far_corner[1]) - cheb(sx, sy, far_corner[0], far_corner[1])) * 0.1
        else:
            # primary: run away (prefer larger distance)
            score = (d * 20 - 1000) + (d - dc) * 50
            # secondary: head toward farthest corner from opponent while staying away
            tc = max(corners, key=lambda c: cheb(c[0], c[1], ox, oy))
            score += (cheb(nx, ny, tc[0], tc[1]) - cheb(sx, sy, tc[0], tc[1])) * 0.25

        # deterministic tie-break: lexicographically smallest (dx,dy) among equals
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]