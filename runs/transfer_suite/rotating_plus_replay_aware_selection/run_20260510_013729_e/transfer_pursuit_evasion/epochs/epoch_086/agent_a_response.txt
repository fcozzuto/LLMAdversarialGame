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
    pursuer = (not self_ev) or opp_ev  # if we're not evader, chase; else evade unless opponent evades too

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
    best_score = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        dist = cheb(nx, ny, ox, oy)

        # tie-break: avoid moving into tighter "corner" to reduce being sandwiched by obstacles
        corner_bias = (nx == 0) + (nx == w - 1) + (ny == 0) + (ny == h - 1)
        # For evasion also bias toward farther from the "most relevant" corner relative to opponent
        corners = [(0,0),(0,h-1),(w-1,0),(w-1,h-1)]
        # choose farthest corner from opponent deterministically
        far_corner = max(corners, key=lambda c: (abs(c[0]-ox)+abs(c[1]-oy), -c[0], -c[1]))
        man_to_far = abs(nx - far_corner[0]) + abs(ny - far_corner[1])

        if pursuer:
            score = (-dist, -corner_bias, man_to_far)
        else:
            score = (dist, -corner_bias, man_to_far)

        if best is None or score > best_score:
            best = (dx, dy)
            best_score = score

    if best is None:
        return [0, 0]
    return [best[0], best[1]]