def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    self_role = str(observation.get("self_role") or "").lower()
    opp_role = str(observation.get("opponent_role") or "").lower()
    we_evader = ("evader" in self_role) or ("pursuer" not in self_role and "evader" in opp_role)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Immediate contact avoidance (evader) / pursuit preference (pursuer)
    base = cheb(sx, sy, ox, oy)
    best_move = (0, 0)
    best_score = None

    # Deterministic tie-break: iterate in fixed order; set strict comparisons
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        d = cheb(nx, ny, ox, oy)
        # Explore further: one-step lookahead against obstacles only (no randomness)
        worst_next_block = 0
        if we_evader:
            # Prefer moves that keep away even if opponent "incentivizes" closing; penalize if we have no safe exits
            for ddx, ddy in moves:
                tx, ty = nx + ddx, ny + ddy
                if not ok(tx, ty):
                    worst_next_block += 1
            score = (d - base) * 10 + d * 2 - worst_next_block * 0.6
            # Extra deterrent: don't move into very close range
            if d <= 1:
                score -= 50
            # Avoid "lanes" that align closely with opponent (king-move line)
            if cheb(nx, ny, ox, oy) == cheb(sx, sy, ox, oy) and (nx == ox or ny == oy):
                score -= 3
        else:
            # Pursuer: minimize distance and avoid getting stuck behind obstacles
            for ddx, ddy in moves:
                tx, ty = nx + ddx, ny + ddy
                if ok(tx, ty):
                    worst_next_block -= 1  # more exits is better
            score = (base - d) * 12 + (d == 0) * 200 + (-worst_next_block) * 0.4
            if d <= 1:
                score += 20
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]