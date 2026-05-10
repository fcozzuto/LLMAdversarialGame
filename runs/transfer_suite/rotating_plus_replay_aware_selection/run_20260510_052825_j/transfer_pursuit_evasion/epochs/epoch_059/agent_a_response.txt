def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    self_role = str(observation.get("self_role", "")).lower()
    opponent_role = str(observation.get("opponent_role", "")).lower()
    self_is_evader = ("evad" in self_role) or (self_role == "evader") or ("purs" in opponent_role)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    # fixed-order tie-break via iteration order

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    def edge_penalty(x, y):
        # discourage hugging edges a bit (helps against zigzag turns)
        return min(x, y, w - 1 - x, h - 1 - y)

    def obstacle_risk(x, y):
        # penalize being adjacent to obstacles (local clearance)
        r = 0
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if (nx, ny) in obstacles:
                r += 1
        return r

    best_score = None
    best_move = [0, 0]
    for dx, dy in deltas:
        tx, ty = sx + dx, sy + dy
        if not (0 <= tx < w and 0 <= ty < h):
            continue
        if (tx, ty) in obstacles:
            continue

        d2 = dist2(tx, ty, ox, oy)
        # primary objective: distance for evader, closeness for pursuer
        primary = d2 if self_is_evader else -d2
        # secondary: keep local clearance and avoid extreme edges
        sec = 0.35 * edge_penalty(tx, ty) - 0.6 * obstacle_risk(tx, ty)

        # if pursuer, also bias toward reducing Manhattan to stabilize zigzag pursuit
        if not self_is_evader:
            man = abs(tx - ox) + abs(ty - oy)
            primary += -0.15 * man
        else:
            # if evader, bias toward increasing Manhattan to prevent corner trapping
            man = abs(tx - ox) + abs(ty - oy)
            primary += 0.08 * man

        score = primary + sec
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move