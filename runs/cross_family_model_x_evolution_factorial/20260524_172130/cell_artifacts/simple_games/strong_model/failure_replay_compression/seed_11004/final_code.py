def choose_move(observation):
    def sgn(v):
        return 0 if v == 0 else (1 if v > 0 else -1)

    def clamp01(x):
        return -1 if x < -1 else (1 if x > 1 else x)

    def pos2(obj, default=(0, 0)):
        if isinstance(obj, (list, tuple)) and len(obj) >= 2:
            return obj[0], obj[1]
        return default

    def best_step_toward(target, sx, sy):
        tx, ty = pos2(target, (sx, sy))
        return [sgn(tx - sx), sgn(ty - sy)]

    env = observation.get("environment_name", "resource_collection")
    self_pos = pos2(observation.get("self_position", (0, 0)))
    opp_pos = pos2(observation.get("opponent_position", (0, 0)))
    sx, sy = self_pos
    ox, oy = opp_pos
    gw = observation.get("grid_width", 0) or 0
    gh = observation.get("grid_height", 0) or 0

    if env == "pursuit_evasion":
        role = observation.get("self_role", "pursuer")
        if role == "pursuer":
            if abs(ox - sx) + abs(oy - sy) <= 1:
                return [sgn(ox - sx), sgn(oy - sy)]
            return best_step_toward((ox, oy), sx, sy)
        corners = []
        if gw > 0 and gh > 0:
            corners = [(0, 0), (0, gh - 1), (gw - 1, 0), (gw - 1, gh - 1)]
        else:
            corners = [(-10, -10), (-10, 10), (10, -10), (10, 10)]
        target = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))
        return best_step_toward(target, sx, sy)

    if env == "territory_control":
        candidates = (
            observation.get("unclaimed_cells")
            or observation.get("opponent_territory")
            or observation.get("frontier_cells")
            or []
        )
        if candidates:
            best = min(candidates, key=lambda item: abs(pos2(item)[0] - sx) + abs(pos2(item)[1] - sy))
            return best_step_toward(best, sx, sy)

        if gw > 0 and gh > 0:
            center = (gw // 2, gh // 2)
            return best_step_toward(center, sx, sy)

        return [0, 0]

    resources = observation.get("resources") or observation.get("resource_positions") or []
    if resources:
        best = min(resources, key=lambda item: abs(pos2(item)[0] - sx) + abs(pos2(item)[1] - sy))
        return best_step_toward(best, sx, sy)

    # Fallbacks: prefer center, then away from opponent if close.
    if gw > 0 and gh > 0:
        center = (gw // 2, gh // 2)
        if abs(ox - sx) + abs(oy - sy) <= 2:
            away = (sx - sgn(ox - sx), sy - sgn(oy - sy))
            return [clamp01(away[0] - sx), clamp01(away[1] - sy)]
        return best_step_toward(center, sx, sy)

    if abs(ox - sx) + abs(oy - sy) <= 1:
        return [sgn(sx - ox), sgn(sy - oy)]

    return [0, 0]
