def choose_move(observation):
    gw = int(observation["grid_width"])
    gh = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])
    resources = observation.get("resources") or []
    obs = {(int(p[0]), int(p[1])) for p in (observation.get("obstacles") or [])}

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def dist8(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        ax = dx if dx >= 0 else -dx
        ay = dy if dy >= 0 else -dy
        return ax if ax > ay else ay

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        score = 0
        for r in resources:
            rx, ry = int(r[0]), int(r[1])
            if (rx, ry) in obs or not inb(rx, ry):
                continue
            d_ours = dist8(nx, ny, rx, ry)
            d_opp = dist8(ox, oy, rx, ry)
            # Intercept/deny: prioritize states where we are closer than opponent; then minimize our remaining distance.
            score += (d_opp - d_ours) * 10 - d_ours
        # If there are no valid resources after filtering, keep neutral.
        if score == 0:
            score = -dist8(nx, ny, ox, oy) * 0.1
        if best_score is None or score > best_score or (score == best_score and (nx, ny) < (sx + best_move[0], sy + best_move[1])):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]