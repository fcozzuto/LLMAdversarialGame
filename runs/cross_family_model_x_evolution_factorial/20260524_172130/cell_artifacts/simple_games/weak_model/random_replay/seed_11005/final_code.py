def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    env = observation.get("environment_name", "resource_collection")
    
    def get_field(field, default=None):
        return observation.get(field, default)
    
    def move_toward(target_x, target_y):
        dx, dy = 0, 0
        if target_x > sx:
            dx = 1
        elif target_x < sx:
            dx = -1
        if target_y > sy:
            dy = 1
        elif target_y < sy:
            dy = -1
        return [dx, dy]
    
    # Territory control
    if env == "territory_control":
        targets = get_field("unclaimed_cells") or get_field("opponent_territory") or []
        if targets:
            best = min(targets, key=lambda item: abs(item[0]-sx)+abs(item[1]-sy))
            return move_toward(best[0], best[1])
        else:
            return [0, 0]
    
    # Pursuit-evasion
    if env == "pursuit_evasion":
        role = get_field("self_role", "pursuer")
        if role == "pursuer":
            return move_toward(ox, oy)
        else:
            dx, dy = 0, 0
            if ox >= sx:
                dx = -1
            elif ox <= sx:
                dx = 1
            if oy >= sy:
                dy = -1
            elif oy <= sy:
                dy = 1
            return [dx, dy]
    
    # Resource collection
    resources = get_field("resources") or []
    if resources:
        best_res = min(resources, key=lambda item: abs(item[0]-sx)+abs(item[1]-sy))
        return move_toward(best_res[0], best_res[1])
    else:
        # No resources, move toward opponent or stay still
        return move_toward(ox, oy)
