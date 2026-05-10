def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    w, h = observation["grid_width"], observation["grid_height"]

    if not resources:
        return [0, 0]

    def pick_target():
        best = None
        best_key = None
        for rx, ry in resources:
            self_d = abs(rx - sx) + abs(ry - sy)
            opp_d = abs(rx - ox) + abs(ry - oy)
            reachable_flag = 0 if self_d <= opp_d else 1  # 0 better
            key = (reachable_flag, self_d, -opp_d, rx, ry)
            if best_key is None or key < best_key:
                best_key = key
                best = (rx, ry)
        return best

    tx, ty = pick_target()

    def cell_ok(nx, ny):
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            return False
        return (nx, ny) not in obstacles

    best_move = (0, 0)
    best_score = None

    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not cell_ok(nx, ny):
                continue
            self_d = abs(tx - nx) + abs(ty - ny)
            opp_d = abs(tx - ox) + abs(ty - oy)
            # Prefer getting closer to target, and only move if we keep/restore advantage.
            advantage = (opp_d - self_d)  # higher is better
            dist_progress = (abs(tx - sx) + abs(ty - sy)) - self_d
            # Discourage moving away; discourage approaching opponent directly.
            opp_reach = max(abs(nx - ox) + abs(ny - oy), 1)
            opp_penalty = 6.0 / opp_reach
            score = (1 if dist_progress >= 0 else 0, advantage, dist_progress, -self_d, -opp_penalty, -abs(dx), -abs(dy))
            if best_score is None or score > best_score:
                best_score = score
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]