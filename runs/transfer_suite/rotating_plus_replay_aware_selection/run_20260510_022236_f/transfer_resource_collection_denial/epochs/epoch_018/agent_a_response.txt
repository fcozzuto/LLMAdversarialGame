def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((int(x), int(y)) for x, y in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0, -10**9, -10**9)  # dx,dy,score,break

    if not resources:
        return [0, 0]

    # Change in behavior vs previous: stronger obstacle-respecting scoring + slight preference to "deny" opponent-closer resources.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        best_adv = -10**9
        best_opp_deny = -10**9
        nearest_self = 10**9
        for rx, ry in resources:
            if not inb(rx, ry):
                continue
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            adv = od - sd
            if adv > best_adv:
                best_adv = adv
            # Deny: how much closer opponent is than we are (prefer making that smaller/negative).
            opp_deny = sd - od
            if opp_deny > best_opp_deny:
                best_opp_deny = opp_deny
            if sd < nearest_self:
                nearest_self = sd

        # If already on a resource, stay is typically best (but move scoring still works); keep deterministic.
        tie_break = -nearest_self
        score = best_adv * 100 + tie_break + best_opp_deny * 2
        cand = (dx, dy, score, tie_break)
        if cand[2] > best_move[2] or (cand[2] == best_move[2] and cand[3] > best_move[3]):
            best_move = cand

    return [int(best_move[0]), int(best_move[1])]