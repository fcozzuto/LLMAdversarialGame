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
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    def clamp(v, lo, hi):
        return lo if v < lo else hi if v > hi else v

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked_after_move(dx, dy):
        nx, ny = sx + dx, sy + dy
        return not in_bounds(nx, ny) or (nx, ny) in obstacles

    target = max(corners, key=lambda c: dist2(c[0], c[1], ox, oy)) if self_is_evader else None

    best = [0, 0]
    bestv = None

    for dx, dy in deltas:
        if dx == 0 and dy == 0:
            # discourage standing if a valid move exists
            stand_penalty = 1 if any(not blocked_after_move(mx, my) for mx, my in deltas if (mx, my) != (0, 0)) else 0
        else:
            stand_penalty = 0

        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        d_opp = dist2(nx, ny, ox, oy)

        # Cut-off / wall-running counter: prefer moving parallel to opponent-wall tendency by aligning
        # with farthest corner direction for evader, or with the opponent position for pursuer.
        if self_is_evader:
            # maximize distance, but also progress toward a far corner to escape the wall-run corridors
            goal = target
            d_goal = dist2(nx, ny, goal[0], goal[1])
            # also push away from opponent
            score = (d_opp * 3) - d_goal - stand_penalty
        else:
            # minimize distance to opponent; lightly prefer moves that reduce both dx and dy magnitude (diagonal)
            d_opp_cur = dist2(sx, sy, ox, oy)
            score = -d_opp - (abs((nx - ox)) + abs((ny - oy))) // 2
            if score == 0 and d_opp == d_opp_cur:
                score -= stand_penalty

        # Deterministic tie-break: prefer greater (or smaller) move closeness to opponent direction sign
        if bestv is None or score > bestv:
            bestv = score
            best = [dx, dy]
        elif bestv is not None and score == bestv:
            # tie-break by favoring diagonal when possible, then lexicographic
            if (abs(dx) + abs(dy), -dx, -dy) > (abs(best[0]) + abs(best[1]), -best[0], -best[1]):
                best = [dx, dy]

    return [int(best[0]), int(best[1])]