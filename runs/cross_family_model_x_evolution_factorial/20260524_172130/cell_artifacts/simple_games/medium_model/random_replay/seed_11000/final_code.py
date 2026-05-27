def choose_move(observation):
    # Defensive access to observation with defaults
    def get_int(vals, key, default=0):
        try:
            v = vals.get(key)
        except AttributeError:
            v = None
        if isinstance(v, int):
            return v
        return default

    # Initialize position
    pos_x = None
    pos_y = None
    if isinstance(observation, dict):
        pos_x = get_int(observation, 'x', None)
        pos_y = get_int(observation, 'y', None)
        if pos_x is None:
            pos_x = get_int(observation, 'pos_x', 0)
        if pos_y is None:
            pos_y = get_int(observation, 'pos_y', 0)

    if pos_x is None:
        pos_x = 0
    if pos_y is None:
        pos_y = 0

    if not isinstance(observation, dict):
        observation = {}

    # Helper to normalize a candidate delta
    def norm(dx, dy):
        if dx in (-1, 0, 1) and dy in (-1, 0, 1):
            return [dx, dy]
        return None

    # Try to see a direct target delta
    target_dx = observation.get('target_dx')
    target_dy = observation.get('target_dy')
    if isinstance(target_dx, int) and isinstance(target_dy, int):
        dx = 1 if target_dx > 0 else -1 if target_dx < 0 else 0
        dy = 1 if target_dy > 0 else -1 if target_dy < 0 else 0
        m = norm(dx, dy)
        if m is not None:
            return m

    # Try to see a known enemy position relative
    enemy_dx = observation.get('enemy_dx')
    enemy_dy = observation.get('enemy_dy')
    if isinstance(enemy_dx, int) and isinstance(enemy_dy, int):
        dx = -1 if enemy_dx > 0 else 1 if enemy_dx < 0 else 0
        dy = -1 if enemy_dy > 0 else 1 if enemy_dy < 0 else 0
        m = norm(dx, dy)
        if m is not None:
            return m

    # Try to see a resource direction
    resource_dx = observation.get('resource_dx')
    resource_dy = observation.get('resource_dy')
    if isinstance(resource_dx, int) and isinstance(resource_dy, int):
        dx = 1 if resource_dx > 0 else -1 if resource_dx < 0 else 0
        dy = 1 if resource_dy > 0 else -1 if resource_dy < 0 else 0
        m = norm(dx, dy)
        if m is not None:
            return m

    # Territory control hints
    control_dx = observation.get('control_dx')
    control_dy = observation.get('control_dy')
    if isinstance(control_dx, int) and isinstance(control_dy, int):
        dx = 1 if control_dx > 0 else -1 if control_dx < 0 else 0
        dy = 1 if control_dy > 0 else -1 if control_dy < 0 else 0
        m = norm(dx, dy)
        if m is not None:
            return m

    # Fallback: simple deterministic pattern based on position
    pattern = [(1,0),(0,1),(-1,0),(0,-1)]
    idx = (pos_x + pos_y) % len(pattern)
    dx, dy = pattern[idx]
    m = norm(dx, dy)
    if m is not None:
        return m

    # Final safe default
    return [0, 0]
