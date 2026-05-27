def choose_move(observation):
    def _sgn(v):
        return 0 if v == 0 else (1 if v > 0 else -1)

    def _pos(v):
        if isinstance(v, (list, tuple)) and len(v) >= 2:
            return v[0], v[1]
        return None

    def _clamp_move(dx, dy):
        return [_sgn(dx), _sgn(dy)]

    def _best_step_toward(sx, sy, tx, ty):
        return _clamp_move(tx - sx, ty - sy)

    env = observation.get("environment_name", "resource_collection")
    self_pos = _pos(observation.get("self_position")) or (0, 0)
    opp_pos = _pos(observation.get("opponent_position")) or self_pos
    sx, sy = self_pos
    ox, oy = opp_pos
    gw = observation.get("grid_width", 0)
    gh = observation.get("grid_height", 0)

    if env == "pursuit_evasion":
        role = observation.get("self_role", "pursuer")
        if role == "pursuer":
            return _best_step_toward(sx, sy, ox, oy)

        corners = []
        if gw and gh:
            corners = [(0, 0), (0, gh - 1), (gw - 1, 0), (gw - 1, gh - 1)]
        if corners:
            target = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))
            return _best_step_toward(sx, sy, target[0], target[1])
        return _best_step_toward(sx, sy, sx + _sgn(sx - ox), sy + _sgn(sy - oy))

    if env == "territory_control":
        candidates = []
        for key in ("unclaimed_cells", "opponent_territory", "neutral_cells", "frontier_cells"):
            items = observation.get(key) or []
            for item in items:
                p = _pos(item)
                if p is not None:
                    candidates.append(p)
        if candidates:
            best = min(candidates, key=lambda c: abs(c[0] - sx) + abs(c[1] - sy))
            return _best_step_toward(sx, sy, best[0], best[1])

        # Fallback: move away from opponent if pressured, else toward center-ish.
        if gw and gh:
            cx, cy = gw // 2, gh // 2
            if abs(sx - ox) + abs(sy - oy) <= 2:
                return _best_step_toward(sx, sy, sx + _sgn(sx - ox), sy + _sgn(sy - oy))
            return _best_step_toward(sx, sy, cx, cy)
        return [0, 0]

    resources = observation.get("resources") or observation.get("resource_positions") or []
    res_pos = []
    for item in resources:
        p = _pos(item)
        if p is not None:
            res_pos.append(p)

    if res_pos:
        best = min(res_pos, key=lambda c: abs(c[0] - sx) + abs(c[1] - sy))
        return _best_step_toward(sx, sy, best[0], best[1])

    # Generic fallback: if opponent is near, step away; otherwise drift toward origin/center.
    if abs(sx - ox) + abs(sy - oy) <= 2:
        return _best_step_toward(sx, sy, sx + _sgn(sx - ox), sy + _sgn(sy - oy))
    if gw and gh:
        return _best_step_toward(sx, sy, gw // 2, gh // 2)
    return [0, 0]
