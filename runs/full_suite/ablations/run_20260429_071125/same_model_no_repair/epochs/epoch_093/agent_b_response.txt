def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = int(observation["grid_width"]), int(observation["grid_height"])
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cd(a, b, c, d):
        ax, ay = a, b
        bx, by = c, d
        dx = ax - bx
        dy = ay - by
        return (dx * dx + dy * dy) ** 0.5

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Pick a resource where we are likely to arrive earlier than opponent
    best_r = resources[0]
    best_key = (10**9, 10**9, 10**9)
    for r in resources:
        rx, ry = r
        du = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # primary: smaller du-do (we closer); tie: smaller du; tie: deterministic coordinate
        key = (du - do, du, rx + 100 * ry)
        if key < best_key:
            best_key = key
            best_r = r
    tx, ty = best_r

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue

        # Heuristic: maximize closeness to target and increase separation from opponent.
        du = cheb(nx, ny, tx, ty)
        do = cheb(nx, ny, ox, oy)
        # Avoid stepping into squares that make us closer to opponent than opponent is to that square
        # (reduces giving opponent contests)
        opp_to_here = cheb(ox, oy, nx, ny)
        dist_adv = do - opp_to_here

        # Add small preference for moves that reduce target distance.
        cur_du = cheb(sx, sy, tx, ty)
        approach = cur_du - du

        val = (-2.2 * du) + (1.1 * do) + (0.6 * dist_adv) + (0.35 * approach)
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]