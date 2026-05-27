def choose_move(observation):
    def clamp_step(v):
        return 0 if v == 0 else (1 if v > 0 else -1)

    def pos(v):
        if isinstance(v, (list, tuple)) and len(v) >= 2:
            return v[0], v[1]
        return None

    def manhattan(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def step_toward(src, dst):
        return [clamp_step(dst[0] - src[0]), clamp_step(dst[1] - src[1])]

    def step_away(src, dst):
        return [clamp_step(src[0] - dst[0]), clamp_step(src[1] - dst[1])]

    def best_by_distance(items, src, reverse=False):
        best_item = None
        best_val = None
        for it in items or []:
            p = pos(it)
            if p is None:
                continue
            d = manhattan(src, p)
            if best_item is None or (d < best_val if not reverse else d > best_val):
                best_item = p
                best_val = d
        return best_item

    env = observation.get("environment_name", "resource_collection")
    self_pos = pos(observation.get("self_position")) or (0, 0)
    opp_pos = pos(observation.get("opponent_position")) or self_pos
    w = observation.get("grid_width", 0) or 0
    h = observation.get("grid_height", 0) or 0

    role = observation.get("self_role", "")

    if env == "pursuit_evasion":
        if role == "evader":
            corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
            target = best_by_distance(corners, opp_pos, reverse=True)
            if target is None:
                return step_away(self_pos, opp_pos)
            return step_toward(self_pos, target)
        return step_toward(self_pos, opp_pos)

    if env == "territory_control":
        targets = observation.get("unclaimed_cells") or observation.get("opponent_territory") or observation.get("frontier") or []
        target = best_by_distance(targets, self_pos)
        if target is not None:
            return step_toward(self_pos, target)
        center = (w // 2, h // 2)
        return step_toward(self_pos, center)

    resources = observation.get("resources") or observation.get("resource_cells") or []
    target = best_by_distance(resources, self_pos)
    if target is not None:
        opp_target = best_by_distance(resources, opp_pos)
        if opp_target is not None and manhattan(self_pos, target) > manhattan(opp_pos, target):
            return step_away(self_pos, opp_pos)
        return step_toward(self_pos, target)

    if w and h:
        center = (w // 2, h // 2)
        return step_toward(self_pos, center)

    return step_away(self_pos, opp_pos)
