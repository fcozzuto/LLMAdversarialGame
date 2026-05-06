def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def dist(x1, y1, x2, y2):
        dx = x2 - x1
        if dx < 0: dx = -dx
        dy = y2 - y1
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_key = None

    for dxm, dym in moves:
        nx, ny = sx + dxm, sy + dym
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue

        myd = None
        target_key = None

        for rx, ry in resources:
            my = dist(nx, ny, rx, ry)
            op = dist(ox, oy, rx, ry)
            # Prefer resources where we can beat (or nearly beat) the denier; otherwise disrupt.
            beat = 1 if op <= my else 0
            # Key: maximize disruption/advantage; break ties by faster and more central (lower coords lexicographically).
            key = (beat, op - my, -(my), -abs(rx - 3.5) - abs(ry - 3.5), -rx, -ry)
            if target_key is None or key > target_key:
                target_key = key
                myd = my

        # Small preference for not moving away from current best (robustness).
        move_penalty = -dist(nx, ny, sx, sy)
        final_key = (target_key[0], target_key[1], target_key[2], move_penalty, target_key[4], target_key[5])
        if best_key is None or final_key > best_key:
            best_key = final_key
            best = (dxm, dym)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]