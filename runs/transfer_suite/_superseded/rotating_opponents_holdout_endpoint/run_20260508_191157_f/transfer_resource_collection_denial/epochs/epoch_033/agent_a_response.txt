def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    w, h = observation["grid_width"], observation["grid_height"]

    if not resources:
        return [0, 0]

    def best_resource():
        best = None
        best_key = None
        for rx, ry in resources:
            self_d = abs(rx - sx) + abs(ry - sy)
            opp_d = abs(rx - ox) + abs(ry - oy)
            # Prefer resources we can reach not later than opponent; otherwise steal by maximizing lead.
            reachable_flag = 0 if self_d <= opp_d else 1
            # Penalize being "too far" overall, and tie-break deterministically by position.
            key = (reachable_flag, self_d, -opp_d, rx, ry)
            if best_key is None or key < best_key:
                best_key = key
                best = (rx, ry)
        return best

    tx, ty = best_resource()

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        # Aim to reduce distance to target; small bias to approach resources and avoid opponent.
        cur_d = abs(tx - sx) + abs(ty - sy)
        new_d = abs(tx - nx) + abs(ty - ny)
        new_opp_d = abs(tx - ox) + abs(ty - oy)  # static, keeps deterministic; bias by our movement only
        candidates.append(((new_d - cur_d), new_d, dx, dy, nx, ny))

    if not candidates:
        # If blocked, allow staying (engine will keep us in place anyway).
        return [0, 0]

    candidates.sort(key=lambda t: (t[0], t[1], t[2], t[3]))
    _, _, dx, dy, _, _ = candidates[0]
    return [dx, dy]