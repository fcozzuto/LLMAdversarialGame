def choose_move(observation):
    # Defensive, robust policy suitable for multiple observation types.
    # Aim: move towards or keep distance from opponent with simple, safe choices.

    # Extract current position
    pos = observation.get("self_position", observation.get("position", (0, 0)))
    try:
        x = int(pos[0]); y = int(pos[1])
    except Exception:
        x, y = 0, 0

    # Try to obtain opponent position from multiple possible keys
    ox = oy = None
    opp_keys = [
        "opponent_position",
        "opponent",
        "enemy_position",
        "opponent_pos"
    ]
    for k in opp_keys:
        val = observation.get(k)
        if isinstance(val, (list, tuple)) and len(val) >= 2:
            try:
                ox = int(val[0]); oy = int(val[1])
                break
            except Exception:
                pass
        if isinstance(val, dict):
            try:
                ox = int(val.get("x", 0)); oy = int(val.get("y", 0))
                break
            except Exception:
                pass
        if val is None:
            continue

    # Fallback to explicit fields if present
    if ox is None or oy is None:
        try:
            ox = int(observation.get("opponent_position_x"))
            oy = int(observation.get("opponent_position_y"))
        except Exception:
            ox = oy = None

    # If opponent info invalid, perform a safe neutral move (stay)
    if not isinstance(ox, int) or not isinstance(oy, int):
        return [0, 0]

    # Define candidate moves (including stay)
    candidates = [
        (0, 0),
        (1, 0), (-1, 0),
        (0, 1), (0, -1),
        (1, 1), (1, -1),
        (-1, 1), (-1, -1)
    ]

    # Helper: Manhattan distance to opponent after move
    def dist(dx, dy):
        nx, ny = x + dx, y + dy
        return abs(ox - nx) + abs(oy - ny)

    # Score and collect best moves
    scored = []
    for dx, dy in candidates:
        if dx in (-1, 0, 1) and dy in (-1, 0, 1):
            scored.append((dist(dx, dy), dx, dy))

    if not scored:
        return [0, 0]

    # Sort by distance; deterministic tie-breaker
    scored.sort()
    best_dist = scored[0][0]
    best_choices = [(dx, dy) for d, dx, dy in scored if d == best_dist]

    # Return the first best choice deterministically
    dx, dy = best_choices[0]
    return [dx, dy]
