def choose_move(observation):
    # Defensive defaults for current position
    x = observation.get("player_x", 0)
    y = observation.get("player_y", 0)

    # Helper to compute step from delta-like evidence
    def step_from(dz, dy=None):
        if dy is None:
            dy = dz
        # Normalize to -1, 0, or 1
        sdx = int((dz > 0) - (dz < 0))
        sdy = int((dy > 0) - (dy < 0))
        return [sdx, sdy]

    # 1) If there is a general target hint, move toward it
    target_dx = observation.get("target_dx", None)
    target_dy = observation.get("target_dy", None)
    if target_dx is not None and target_dy is not None:
        dx = int((target_dx > 0) - (target_dx < 0))
        dy = int((target_dy > 0) - (target_dy < 0))
        if dx != 0 or dy != 0:
            return [dx, dy]

    # 2) Resource collection cues
    cargo_dx = observation.get("resource_dx", None)
    cargo_dy = observation.get("resource_dy", None)
    if cargo_dx is not None and cargo_dy is not None:
        dx = int((cargo_dx > 0) - (cargo_dx < 0))
        dy = int((cargo_dy > 0) - (cargo_dy < 0))
        if dx != 0 or dy != 0:
            return [dx, dy]

    # 3) Pursuit/Evasion hints
    evade_dx = observation.get("evade_dx", None)
    evade_dy = observation.get("evade_dy", None)
    if evade_dx is not None and evade_dy is not None:
        dx = int((evade_dx > 0) - (evade_dx < 0))
        dy = int((evade_dy > 0) - (evade_dy < 0))
        if dx != 0 or dy != 0:
            return [dx, dy]

    # 4) Territory control hints
    control_dx = observation.get("control_dx", None)
    control_dy = observation.get("control_dy", None)
    if control_dx is not None and control_dy is not None:
        dx = int((control_dx > 0) - (control_dx < 0))
        dy = int((control_dy > 0) - (control_dy < 0))
        if dx != 0 or dy != 0:
            return [dx, dy]

    # 5) If nothing is known, make a small deterministic exploration move
    for dx, dy in ((1, 0), (0, 1), (-1, 0), (0, -1), (0, 0)):
        return [dx, dy]

    return [0, 0]
