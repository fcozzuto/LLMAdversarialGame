def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]
    if any(rx == sx and ry == sy for rx, ry in resources):
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Evaluate this move by the best resource we could potentially secure.
        # Primary: max "lead" (opp distance - self distance).
        # Secondary: smaller self distance to that resource.
        # Tertiary: break ties toward cells that are closer overall.
        best_lead = -10**18
        best_self_dist = 10**18
        best_rank = 10**18

        for i, (rx, ry) in enumerate(resources):
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            lead = od - sd
            if lead > best_lead or (lead == best_lead and (sd < best_self_dist or (sd == best_self_dist and i < best_rank))):
                best_lead = lead
                best_self_dist = sd
                best_rank = i

        # If we can secure (strict lead), prioritize that heavily.
        if best_lead >= 1:
            val = 10**6 * best_lead - best_self_dist
        else:
            # Otherwise, minimize our distance to the best resource, but still try to increase lead.
            val = 1000 * best_lead - best_self_dist

        # Small deterministic bias to prefer staying if equal to reduce oscillations
        if val > best_val or (val == best_val and (dx == 0 and dy == 0) and best_move != (0, 0)):
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]