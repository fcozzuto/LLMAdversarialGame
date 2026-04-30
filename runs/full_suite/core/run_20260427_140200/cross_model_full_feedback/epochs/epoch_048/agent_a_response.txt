def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    me = observation.get("self_position", [0, 0]) or [0, 0]
    opp = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(me[0]), int(me[1])
    ox, oy = int(opp[0]), int(opp[1])

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
        resources = [(sx, sy)]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    opp_pos = (ox, oy)
    # Pick a target where we can get there meaningfully earlier than opponent
    best_target = None
    best_key = None
    for t in resources:
        d_me = dist((sx, sy), t)
        d_opp = dist(opp_pos, t)
        # Prioritize resources we are closer to than opponent by the largest margin.
        # Secondarily prioritize actual distance (closer is better).
        key = (d_opp - d_me, -d_me)
        if best_key is None or key > best_key:
            best_key = key
            best_target = t

    tx, ty = best_target
    best_move = (0, 0)
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        nd_me = dist((nx, ny), (tx, ty))
        nd_opp = dist(opp_pos, (tx, ty))
        # Value: reduce our distance to target, ensure we don't hand the target to opponent.
        # Also avoid getting too close to opponent (helps survival/capture races).
        d_to_opp = dist((nx, ny), opp_pos)
        val = (-nd_me, (nd_opp - nd_me), d_to_opp, -abs(nx - tx) - abs(ny - ty))
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]