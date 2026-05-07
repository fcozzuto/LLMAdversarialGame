def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    res = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def legal(x, y):
        return in_bounds(x, y) and (x, y) not in obstacles

    def dist(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    def clamp01(v):
        return 0.0 if v <= 0 else 1.0 if v >= 1 else v

    best = (0, 0)
    best_val = -10**18

    # Main: pick move that maximizes immediate "race" advantage over opponent for remaining resources
    if res:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            my_to_opp = dist(nx, ny, ox, oy)
            local_best = -10**18
            for rx, ry in res:
                my_d = dist(nx, ny, rx, ry)
                opp_d = dist(ox, oy, rx, ry)
                race = opp_d - my_d  # positive => we are closer than opponent
                # Encourage close-by grabs and strong race advantage; mildly prefer smaller my_d to reduce delay
                val = race * 10.0 - my_d - 0.25 * my_to_opp
                # Strongly prefer immediate collection
                if my_d == 0:
                    val += 10000.0
                # Slightly discourage "ties" where opponent also very close
                if race <= 0 and opp_d <= 1 and my_d <= 1:
                    val -= 2.0
                if val > local_best:
                    local_best = val
            # Extra: if multiple moves tie, pick the one that increases minimum distance to opponent a bit (avoid collisions)
            score = local_best + 0.05 * my_to_opp
            if score > best_val:
                best_val = score
                best = (dx, dy)
            elif score == best_val:
                # deterministic tiebreak: prefer smaller move to reduce risk
                cand = (dx, dy)
                if abs(cand[0]) + abs(cand[1]) < abs(best[0]) + abs(best[1]):
                    best = cand
    else:
        # No resources: maximize distance from opponent while drifting toward the farthest corner from opponent
        corners = [(0, 0), (0, gh - 1), (gw - 1, 0), (gw - 1, gh - 1)]
        target_corner = max(corners, key=lambda c: dist(ox, oy, c[0], c[1]))
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            d_opp = dist(nx, ny, ox, oy)
            d_corner = dist(nx, ny, target_corner[0], target_corner[1])
            score = d_opp * 10.0 - d_corner * 0.1
            if score > best_val:
                best_val = score
                best = (dx, dy)

    return [int(best[0]), int(best[1])]