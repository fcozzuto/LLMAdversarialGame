def choose_move(observation):
    gw = int(observation["grid_width"])
    gh = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])
    resources = [(int(r[0]), int(r[1])) for r in (observation.get("resources") or [])]
    obstacles = {(int(p[0]), int(p[1])) for p in (observation.get("obstacles") or [])}
    turns_remaining = int(observation.get("turns_remaining", 0))

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def dist8(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    cand = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_score = -10**18

    # Prefer staying/going around obstacles deterministically: forbid moving into obstacles
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        # Evaluate best achievable capture from this next position
        local_best = -10**18
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            ds = dist8(nx, ny, rx, ry)
            do = dist8(ox, oy, rx, ry)
            beat = do - ds  # positive means we arrive first (or tie)
            # tie-break: we also value closer overall so we secure earlier if tie
            time_pressure = max(0, (85 - turns_remaining) // 3)
            near_resource = 6 - ds
            # discourage aiming far behind opponent; but allow it if no beat options
            score = beat * 120 + near_resource * 8 - ds * 2 - (beat < 0) * (40 + ds * 3)
            # extra: if we can capture immediately, dominate
            if ds == 0:
                score = 10**9 + (do - ds)
            # extra: avoid walking into lines where opponent is likely to grab (very rough)
            if ry == oy and ds > 0:
                score -= 15
            if score > local_best:
                local_best = score

        # Secondary: if multiple moves tie, pick one that reduces distance to nearest resource
        nearest_after = min(dist8(nx, ny, rx, ry) for rx, ry in resources if (rx, ry) not in obstacles)
        local_total = local_best + (turns_remaining < 25) * (10 * -nearest_after) - (turns_remaining >= 25) * (2 * nearest_after) + (dx == 0 and dy == 0) * (-1)
        if local_total > best_score:
            best_score = local_total
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]