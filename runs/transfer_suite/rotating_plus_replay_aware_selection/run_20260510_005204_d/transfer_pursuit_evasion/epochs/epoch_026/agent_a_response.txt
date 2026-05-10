def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    self_is_evader = ("evad" in role) or ("escape" in role) or ("run" in role) or ("hide" in role) or ("runner" in role)
    # If our role isn't clear, infer from opponent role
    if not self_is_evader and (("evad" in opp_role) or ("escape" in opp_role) or ("run" in opp_role) or ("hide" in opp_role) or ("runner" in opp_role)):
        self_is_evader = True

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def ok(x, y):
        return inb(x, y) and (x, y) not in blocked

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    def obs_penalty(x, y):
        # mild penalty for stepping next to obstacles
        p = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if (nx, ny) in blocked:
                    p += 1
        return p

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = [0, 0]
    best_val = None

    # deterministic tie-break: prefer lower dx, then lower dy if values equal
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        dist = cheb(nx, ny, ox, oy)
        corner_bonus = max(nx, w - 1 - nx) + max(ny, h - 1 - ny)
        penalty = obs_penalty(nx, ny)
        # pursuer minimizes distance; evader maximizes distance
        val = dist + (0.01 * corner_bonus) - (0.03 * penalty) if not self_is_evader else (-dist + (-0.01 * corner_bonus) + (0.03 * penalty))
        if best_val is None:
            best_val = val
            best_move = [dx, dy]
        else:
            if (not self_is_evader and val < best_val) or (self_is_evader and val > best_val):
                best_val = val
                best_move = [dx, dy]
            elif val == best_val:
                if dx < best_move[0] or (dx == best_move[0] and dy < best_move[1]):
                    best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]