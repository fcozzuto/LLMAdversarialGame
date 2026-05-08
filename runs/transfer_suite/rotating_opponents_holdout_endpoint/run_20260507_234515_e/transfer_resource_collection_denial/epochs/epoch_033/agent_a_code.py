def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def md(a, b, c, d): return abs(a - c) + abs(b - d)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obs:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    remaining = observation.get("remaining_resource_count", len(resources))
    close_threshold = 3 if remaining <= 4 else 2

    best_move = None
    best_val = -10**18
    best_t = None

    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        if resources:
            # Competition-focused: maximize (opp_dist - self_dist) to a chosen resource.
            # If near any resource, switch to shortest self path to secure pickup.
            best_res_val = -10**18
            best_res_self_d = 10**9
            best_res_lex = None
            for rx, ry in resources:
                if (rx, ry) in obs:
                    continue
                sd = md(nx, ny, rx, ry)
                od = md(ox, oy, rx, ry)
                # Weighting: secure when already close; otherwise deny opponent lead.
                secure = 6 if sd <= close_threshold else 0
                val = (od - sd) + 0.15 * (secure + (close_threshold - sd)) - 0.01 * (sd)
                if val > best_res_val or (val == best_res_val and (sd, rx, ry) < (best_res_self_d, best_res_lex[0], best_res_lex[1]) if best_res_lex else True):
                    best_res_val = val
                    best_res_self_d = sd
                    best_res_lex = (rx, ry)
            val_total = best_res_val
            t = (best_res_self_d, best_res_lex[0], best_res_lex[1])
        else:
            # No resources: drift toward center and slightly away/toward opponent half to keep tempo.
            center_x = (w - 1) / 2
            center_y = (h - 1) / 2
            val_total = -abs(center_x - nx) - abs(center_y - ny) + 0.01 * (md(nx, ny, ox, oy) * -1)
            t = (abs(center_x - nx) + abs(center_y - ny), nx, ny)

        # Deterministic tie-break: smaller self distance to chosen target, then lexicographic move.
        if (val_total > best_val) or (val_total == best_val and (t, dx, dy) < (best_t, best_move[0], best_move[1]) if best_move is not None and best_t is not None else True):
            best_val = val_total
            best_move = (dx, dy)
            best_t = t

    return [best_move[0], best_move[1]]