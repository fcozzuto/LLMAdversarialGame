def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Precompute opponent distances to each resource
    opp_d = []
    for rx, ry in resources:
        opp_d.append((cheb(ox, oy, rx, ry), rx, ry))

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h): 
            continue
        if (nx, ny) in obstacles:
            continue

        # Choose the best contested resource to move toward: maximize (opp_dist - self_dist)
        best_adv = -10**18
        best_self = 10**9
        for od, rx, ry in opp_d:
            sd = cheb(nx, ny, rx, ry)
            adv = od - sd
            if adv > best_adv:
                best_adv = adv
                best_self = sd

        # If everything is contested (adv <= 0), still push to reduce self distance; add mild center drift
        center = cheb(nx, ny, w // 2, h // 2)
        score = best_adv * 10 - best_self - center * 0.1
        # Micro-tie-break: prefer staying closer to current direction towards better resource
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]