def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for t in observation.get("obstacles") or []:
        if isinstance(t, (list, tuple)) and len(t) >= 2:
            x, y = int(t[0]), int(t[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def is_evader(role):
        r = (role or "").lower()
        return ("evader" in r) or ("runner" in r) or ("evasion" in r) or ("evasive" in r)

    self_evader = is_evader(observation.get("self_role"))
    opp_evader = is_evader(observation.get("opponent_role"))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def obstacle_penalty(x, y):
        # Discourage stepping adjacent to obstacles (but allow if needed).
        pen = 0
        for ax, ay in obstacles:
            if abs(x - ax) <= 1 and abs(y - ay) <= 1:
                pen += 1
        return pen

    def pick_for_agent(myx, myy, targetx, targety, agent_evader):
        # If agent_evader: maximize distance to target; else minimize.
        best_move = None
        best_val = None
        for ddx, ddy in dirs:
            nx, ny = myx + ddx, myy + ddy
            if not valid(nx, ny):
                continue
            d = cheb(nx, ny, targetx, targety)
            p = obstacle_penalty(nx, ny)
            val = d * (1 if agent_evader else -1) + (-p if agent_evader else -p * 2)
            if best_val is None or (val > best_val if agent_evader else val < best_val):
                best_val = val
                best_move = (ddx, ddy)
        return best_move if best_move is not None else (0, 0)

    # If we are evader, run; otherwise pursue with one-step opponent prediction.
    if self_evader:
        dm = pick_for_agent(sx, sy, ox, oy, True)
        return [int(dm[0]), int(dm[1])]

    # Pursuer: choose move minimizing expected distance after opponent responds.
    best = None
    best_key = None
    for ddx, ddy in dirs:
        nx, ny = sx + ddx, sy + ddy
        if not valid(nx, ny):
            continue
        opp_move = pick_for_agent(ox, oy, nx, ny, opp_evader)
        nox, noy = ox + opp_move[0], oy + opp_move[1]
        if not valid(nox, noy):
            nox, noy = ox, oy
        d = cheb(nx, ny, nox, noy)
        # Prefer closer to actual opponent after response, and avoid obstacles.
        key = (d, obstacle_penalty(nx, ny), abs(nx - ox) + abs(ny - oy))
        if best_key is None or key < best_key:
            best_key = key
            best = (ddx, ddy)

    if best is None:
        # Fallback: greedy pursuit with obstacle avoidance
        dm = pick_for_agent(sx, sy, ox, oy, False)
        return [int(dm[0]), int(dm[1])]
    return [int(best[0]), int(best[1])]